# cs3083-project

## How to create a new branch via command line

1. Make sure you are in the main branch.
 ```
 $ git checkout main
 ```
2. Create new branch (which is branched off of main).
```
$ git checkout -b [branch name]
```
3. Start working on your new branch!

## How to commit changes

NOTE: commit often!

1. Make sure there are changes to commit.
```
$ git status
```
2. Add all the files you want to commit (they will be in red, files already
   added to be committed will be green)
```
$ git add [filename]
```
3. Once you've added all your files to be committed, commit it with a message.
```
$ git commit -m "fixed bug in function loop"
```

## How to push changes after you've committed

1. If you've never pushed to the repo, first set upstream to origin.
```
$ git push --set-upstream origin [current branch name]
```

2. Push changes after new commits.
```
$ git push
```

## How to work on someone else's branch

1. Checkout to main branch
```
$ git checkout main
```

2. Fetch all branches
```
$ git fetch origin
```

3. List all branches to find the remote branch you want to work on.
```
$ git branch -a
```

4. Make a copy of the branch that you can work on.
```
$ git checkout -b [branch name] origin/[branch name]
```

5. Pull changes they push to keep your copy of their branch always up to date.
```
$ git pull
```
