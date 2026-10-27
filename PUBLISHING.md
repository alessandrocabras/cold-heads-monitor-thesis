# Publish the Review Snapshot

This directory has its own local Git repository on branch `main`. The parent
working repository, its existing INAF remote and its history are unchanged.
The public repository is https://github.com/alessandrocabras/cold-heads-monitor-thesis.
Its URL is already configured as `origin`. Nothing has been pushed from this copy.

From this directory, inspect and create the first commit:

```powershell
git status --short
git add .
git diff --cached --stat
git commit -m "Prepare Cold Heads Monitor thesis review snapshot"
git tag -a thesis-review-v1 -m "Thesis review snapshot v1"
```

## Browser and Git

The public repository has been created and was verified empty. After the commit
and tag above, push the local branch and review tag:

```powershell
git push -u origin main
git push origin thesis-review-v1
```

Use `git remote -v` to inspect the configured origin. Do not change the parent
repository's existing INAF remote.

The stable revision link for reviewers is:

```text
https://github.com/alessandrocabras/cold-heads-monitor-thesis/tree/thesis-review-v1
```

## GitHub CLI Alternative

If GitHub CLI is already installed, it can authenticate Git's HTTPS connection:

```powershell
gh auth login
gh auth setup-git
```

Then run the Git push commands above. GitHub CLI is optional.
No blanket MIT or other project license has been added by preparing this copy;
the project owners can choose one separately. Third-party theme notices are retained.

Before submission, include the repository URL and review tag in the thesis.
Later corrections should receive a new tag rather than moving the review tag.
