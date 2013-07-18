Contributing
============

We are happy if you add tickets and help us improve the FileBrowser.
However, in order to actually process tickets we need you to follow these guidelines.

1. Run Tests
------------

Before adding a ticket, please do run the tests::

	python manage.py test filebrowser

But be aware that some of the tests are copying files to the location of your storage engine.

2. Add Details
--------------

If you add a ticket, you need to tell us which version of the FileBrowser you're using.
Otherwise we won't be able to review the ticket.

3. Example
----------

Here's an example of a ticket we can easily review::

	Tests: OK/ERROR (Details on errors)
	Version: FileBrowser x.x.x, Grappelli x.x.x, Django x.x

	Text of your ticket, as detailed as possible (code examples might help)