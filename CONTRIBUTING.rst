===============
Contributing
===============

release workflow
----------------

.. code:: bash

    #commit version
    git commit -m "comment"

    #run tests
    tox

    #bumpversion [major | minor | patch]
    bumversion patch

    #push incl. tags
    git push
    git push --tags

