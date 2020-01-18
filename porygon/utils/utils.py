import os
import git

def get_git_root(path=os.getcwd()):

    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root

PROJECT_DIR = get_git_root()
