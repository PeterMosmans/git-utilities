# git-utilities
A collection of handy git hooks / scripts


## hooks

### hooks/pre-commit
This hook is for a local repository, and fires when committing to the repo. It validates files before they are committed.
You can set a variable (`reject`) whether to reject the commit when validation fails, or to allow the invalid file being committed. The default value is `True`, which means that commits will fail when validation fails.

There is currently one validator implemented in the `pre-commit` hook, the XML validator.


### hooks/pre-receive
This hook is for a hosted repository, and fires when people push commits to the repo. It validates files when they are received, and before they are updated.
You can set a variable  (`reject`) whether to reject the update when validation fails, or to allow the invalid file being updated. The default value is `True`, which means that updates will fail when validation fails.

There is currently one validator implemented in the `pre-receive` hook, the XML validator.


## validators

### XML validator
The XML validator checks whether the file has a xml extension, and if so, validates whether it contains correct XML. Note that an empty string is *not* valid XML.




All scripts are GPLv3 licensed.




