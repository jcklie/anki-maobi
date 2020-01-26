# Contributing

Contributions should be submitted by sending a pull request to the project to which you wish to contribute. If your 
contribution addresses an existing bug or feature request listed in the project’s issue tracker, please reference it. 
(If not, consider opening a new issue before sending your pull request.)

Prolific contributors may eventually be granted write access to the code repositories. Access to the repositories is granted on a per-project basis.

## Preparing a pull request

- Before creating a pull request, create an issue in the issue tracker of the project to which you wish to contribute
- Fork the project on GitHub
- Create a branch based on the branch to which you wish to contribute. Normally, you should 
  create this branch from the master branch of the respective project. Do not make 
  changes directly to the master or maintenance branches in your fork. The name of the branch 
  should be e.g. `feature/[ISSUE-NUMBER]-[SHORT-ISSUE-DESCRIPTION]` or
  `bugfix/[ISSUE-NUMBER]-[SHORT-ISSUE-DESCRIPTION]`.
- Now you make changes to your branch. When committing to your branch, use the format shown below 
  for your commit messages. Note that # normally introduces comments in git. You may have to 
  reconfigure git before attempting an interactive rebase and switch it to another comment character.

```
#[ISSUE NUMBER] - [ISSUE TITLE]
[EMPTY LINE]
- [CHANGE 1]
- [CHANGE 2]
- [...]
```

You can create the pull request any time after your first commit. I.e. you do not have to wait 
until you are completely finished with your implementation. Creating a pull request early tells 
other developers that you are actively working on an issue and facilitates asking questions about 
and discussing implementation details.

## Code style

We use [black](https://black.readthedocs.io/en/stable/) to format the Python code. Please run it
before creating a pull request via

    black -l 100 maobi/
    
## Contributor attribution

The `CONTRIBUTORS.txt` file is used to keep track of contributors. It is to be used in favor over author
 attributions in individual files.