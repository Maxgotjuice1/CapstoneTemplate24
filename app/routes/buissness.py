from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Buissness, Comment
from app.classes.forms import BuissnessForm, CommentForm
from flask_login import login_required
import datetime as dt

# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new blog based on what the user put in the form.
# Because this route includes a form that both gets and blogs data it needs the 'methods'
# in the route decorator.
@app.route('/buissness/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def buissnessNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = BuissnessForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newBuissness = Buissness(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            buissness_name = form.buissness_name.data,
            buissness_product = form.buissness_product.data,
            date = form.date.data,
            location = form.location.data,
            favorites = form.favorites.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newBuissness.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('buissness',buissnessID=newBuissness.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('buissnessform.html',form=form)

# This route will get one specific blog and any comments associated with that blog.  
# The blogID is a variable that must be passsed as a parameter to the function and 
# can then be used in the query to retrieve that blog from the database. This route 
# is called when the user clicks a link on bloglist.html template.
# The angle brackets (<>) indicate a variable. 
@app.route('/buissness/<buissnessID>')

# This route will only run if the user is logged in.
@login_required
def buissness(buissnessID):
    # retrieve the blog using the blogID
    thisBuissness = Buissness.objects.get(id=buissnessID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # the blog object (thisBlog in this case) to get all the comments.
    theseComments = Comment.objects(buissness=thisBuissness)
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('buissness.html',buissness=thisBuissness,comments=theseComments)

   


# This route enables a user to edit a blog.  This functions very similar to creating a new 
# blog except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original blog. Read and understand the new blog route 
# before this one. 
@app.route('/buissness/edit/<buissnessID>', methods=['GET', 'POST'])
@login_required
def buissnessEdit(buissnessID):
    editBuissness = Buissness.objects.get(id=buissnessID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editBuissness.author:
        flash("You can't edit a buissness you don't own.")
        return redirect(url_for('buissness',buissnessID=buissnessID))
    # get the form object
    form = BuissnessForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editBuissness.update(
            buissness_name = form.buissness_name.data,
            buissness_product = form.buissness_product.data,
            date = form.date.data,
            location = form.location.data,
            favorites = form.favorites.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('Buissness',buissnessID=buissnessID))

    # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.buissness_name.data = editBuissness.buissness_name
    form.buissness_product.data = editBuissness.buissness_product
    form.date.data = editBuissness.date
    form.location.data = editBuissness.location
    form.favorites.data = editBuissness.favorites


    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('buissnessform.html',form=form)

# This is the route to list all blogs
@app.route('/buissness/list')
@app.route('/buissnesss')
# This means the user must be logged in to see this page
@login_required
def buissnessList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    buissnesss = Buissness.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('buissnesss.html',buissnesss=buissnesss)

# This route will delete a specific blog.  You can only delete the blog if you are the author.
# <blogID> is a variable sent to this route by the user who clicked on the trash can in the 
# template 'blog.html'. 
# TODO add the ability for an administrator to delete blogs. 
@app.route('/buissness/delete/<buissnessID>')
# Only run this route if the user is logged in.
@login_required
def buissnessDelete(buissnessID):
    # retrieve the blog to be deleted using the blogID
    deleteBuissness = Buissness.objects.get(id=buissnessID)
    # check to see if the user that is making this request is the author of the blog.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteBuissness.author:
        # delete the blog using the delete() method from Mongoengine
        deleteBuissness.delete()
        # send a message to the user that the blog was deleted.
        flash('The Blog was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a  you don't own.")
    # Retrieve all of the remaining blogs so that they can be listed.
    buissness = Buissness.objects()  
    # Send the user to the list of remaining blogs.
    return render_template('buissnesss.html',buissness=buissness)

@app.route('/buissness/favorites')
# This means the user must be logged in to see this page
@login_required
def favoritesList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    buissnesss = Buissness.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('buissnessFav.html',buissnesss=buissnesss)