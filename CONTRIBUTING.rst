===============
Contributing
===============

code style&quality
------------------

Please

*  use a new branch per feature
*  push clean/readable commits to simplify merging
*  make use of `logger.debug("it really helps to find tiny bugs")`
*  rather reuse existing code blocks by copy&pasting, than introducing a new style for functions/module

   * I currently prefer stability over code quality. The day of the big re-factoring will come... at some point.

* see `docs/devnotes.md` for additional notes

adding features
---------------

requirements for new features:

*  it must be possible to enable/disable the feature via `config.ini`

   * either by leaving key `label_$feature` empty or
   * a `true`/`false` key

*  it must honor `devmode`. No modifying of userdata when `devmode=true`


tests
-----

Current tests cover the basic CLI functionality and ensure that *destructive* functionality doesn't break the users tasks.

Please add tests for new features if possible.


release workflow
----------------

Package release is automated by CI and started by pushing a tagged commit to master

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

