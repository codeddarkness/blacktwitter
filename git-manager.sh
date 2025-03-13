#!/bin/bash

# Git Repository Manager Script
# This script provides a CLI menu to manage git repositories,
# including fixing branch rename issues

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display the header
display_header() {
    clear
    echo -e "${BLUE}====================================${NC}"
    echo -e "${GREEN}       GIT REPOSITORY MANAGER      ${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo ""
    
    # Display current git status
    echo -e "${YELLOW}Current Git Status:${NC}"
    echo "Repository: $(basename -s .git $(git config --get remote.origin.url 2>/dev/null || echo 'Not configured'))"
    echo "Current Branch: $(git branch --show-current 2>/dev/null || echo 'Not in a git repository')"
    echo "Remote: $(git config --get remote.origin.url 2>/dev/null || echo 'Not configured')"
    
    # Display latest tag if any
    latest_tag=$(git describe --tags --abbrev=0 2>/dev/null)
    if [[ -n $latest_tag ]]; then
        echo "Latest Tag: $latest_tag"
    else
        echo "Latest Tag: None"
    fi
    
    echo -e "${BLUE}====================================${NC}"
    echo ""
}

# Function to check if directory is a git repository
check_git_repo() {
    if ! git rev-parse --is-inside-work-tree &>/dev/null; then
        echo -e "${RED}Error: Not inside a git repository.${NC}"
        echo "Would you like to initialize a git repository here? (y/n)"
        read -r init_choice
        if [[ $init_choice == "y" || $init_choice == "Y" ]]; then
            git init
            echo -e "${GREEN}Git repository initialized.${NC}"
        else
            return 1
        fi
    fi
    return 0
}

# Function to display the main menu
display_menu() {
    echo -e "${GREEN}Select an option:${NC}"
    echo "1. Show git status"
    echo "2. Commit changes"
    echo "3. Push changes"
    echo "4. Pull changes"
    echo "5. Branch management"
    echo "6. Fix branch rename issues"
    echo "7. Merge branches"
    echo "8. Manage tags"
    echo "9. Manage remotes"
    echo "10. View logs"
    echo "11. Manage untracked files"
    echo "0. Exit"
    echo ""
}

# Function to handle git status
git_status() {
    echo -e "\n${YELLOW}Git Status:${NC}"
    git status
    echo ""
    read -p "Press Enter to continue..."
}

# Function to handle commits
commit_changes() {
    echo -e "\n${YELLOW}Files to be committed:${NC}"
    git status --short
    echo ""
    
    echo -e "${GREEN}What would you like to do?${NC}"
    echo "1. Stage all changes"
    echo "2. Stage specific files"
    echo "3. Return to main menu"
    
    read -r commit_choice
    
    case $commit_choice in
        1)
            git add .
            echo -e "${GREEN}All changes staged.${NC}"
            ;;
        2)
            echo -e "${YELLOW}Enter file(s) to stage (space-separated):${NC}"
            read -r files_to_stage
            git add $files_to_stage
            echo -e "${GREEN}Specified files staged.${NC}"
            ;;
        3)
            return
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            read -p "Press Enter to continue..."
            return
            ;;
    esac
    
    echo -e "${YELLOW}Enter commit message:${NC}"
    read -r commit_message
    
    echo -e "${YELLOW}Would you like to create a version tag for this commit? (y/n)${NC}"
    read -r create_tag
    
    if [[ $create_tag == "y" || $create_tag == "Y" ]]; then
        echo -e "${YELLOW}Current tags:${NC}"
        git tag
        
        echo -e "\n${YELLOW}Enter tag version (e.g., v1.0.0):${NC}"
        read -r tag_version
        
        echo -e "${YELLOW}Enter tag message (optional):${NC}"
        read -r tag_message
        
        git commit -m "$commit_message"
        
        if [[ -z $tag_message ]]; then
            git tag $tag_version
        else
            git tag -a $tag_version -m "$tag_message"
        fi
        
        echo -e "${GREEN}Changes committed with tag: $tag_version${NC}"
    else
        git commit -m "$commit_message"
        echo -e "${GREEN}Changes committed.${NC}"
    fi
    
    read -p "Press Enter to continue..."
}

# Function to handle pushing changes
push_changes() {
    current_branch=$(git branch --show-current)
    
    echo -e "\n${YELLOW}Current branch: $current_branch${NC}"
    echo -e "${GREEN}Push to which remote? (default: origin)${NC}"
    read -r remote
    
    if [[ -z $remote ]]; then
        remote="origin"
    fi
    
    echo -e "${GREEN}Set upstream? (y/n) (default: y)${NC}"
    read -r set_upstream
    
    if [[ -z $set_upstream || $set_upstream == "y" || $set_upstream == "Y" ]]; then
        git push -u $remote $current_branch
    else
        git push $remote $current_branch
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to handle pulling changes
pull_changes() {
    echo -e "\n${YELLOW}Pull from which remote? (default: origin)${NC}"
    read -r remote
    
    if [[ -z $remote ]]; then
        remote="origin"
    fi
    
    echo -e "${YELLOW}Pull from which branch? (default: current branch)${NC}"
    read -r branch
    
    if [[ -z $branch ]]; then
        branch=$(git branch --show-current)
    fi
    
    git pull $remote $branch
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to handle branch management
branch_management() {
    echo -e "\n${GREEN}Branch Management:${NC}"
    echo "1. List all branches"
    echo "2. Create new branch"
    echo "3. Switch to branch"
    echo "4. Rename branch"
    echo "5. Delete branch"
    echo "6. Return to main menu"
    
    read -r branch_choice
    
    case $branch_choice in
        1)
            echo -e "\n${YELLOW}Local branches:${NC}"
            git branch
            echo -e "\n${YELLOW}Remote branches:${NC}"
            git branch -r
            ;;
        2)
            echo -e "\n${YELLOW}Enter new branch name:${NC}"
            read -r new_branch
            git checkout -b $new_branch
            echo -e "${GREEN}Created and switched to new branch: $new_branch${NC}"
            ;;
        3)
            echo -e "\n${YELLOW}Available branches:${NC}"
            git branch
            echo -e "\n${YELLOW}Enter branch name to switch to:${NC}"
            read -r switch_branch
            git checkout $switch_branch
            echo -e "${GREEN}Switched to branch: $switch_branch${NC}"
            ;;
        4)
            echo -e "\n${YELLOW}Available branches:${NC}"
            git branch
            echo -e "\n${YELLOW}Enter branch name to rename:${NC}"
            read -r old_branch
            echo -e "${YELLOW}Enter new branch name:${NC}"
            read -r new_branch
            git branch -m $old_branch $new_branch
            echo -e "${GREEN}Renamed branch from $old_branch to $new_branch${NC}"
            ;;
        5)
            echo -e "\n${YELLOW}Available branches:${NC}"
            git branch
            echo -e "\n${YELLOW}Enter branch name to delete:${NC}"
            read -r del_branch
            echo -e "${RED}Are you sure you want to delete branch $del_branch? (y/n)${NC}"
            read -r confirm_delete
            
            if [[ $confirm_delete == "y" || $confirm_delete == "Y" ]]; then
                git branch -d $del_branch
                echo -e "${GREEN}Branch deleted: $del_branch${NC}"
            else
                echo -e "${YELLOW}Branch deletion canceled.${NC}"
            fi
            ;;
        6)
            return
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to fix branch rename issues
fix_branch_rename_issues() {
    echo -e "\n${GREEN}Fix Branch Rename Issues:${NC}"
    echo -e "${YELLOW}This will help fix issues with branch renaming, including 'refusing to delete the current branch' errors.${NC}"
    echo ""
    
    # Get current branch
    current_branch=$(git branch --show-current)
    echo -e "${YELLOW}Current branch: $current_branch${NC}"
    
    # List remotes
    echo -e "\n${YELLOW}Available remotes:${NC}"
    git remote -v | grep "(push)" | awk '{print $1}'
    echo -e "\n${YELLOW}Enter the remote name (default: origin):${NC}"
    read -r remote_name
    
    if [[ -z $remote_name ]]; then
        remote_name="origin"
    fi
    
    # List branches
    echo -e "\n${YELLOW}Current local branches:${NC}"
    git branch
    echo -e "\n${YELLOW}Current remote branches:${NC}"
    git branch -r
    
    echo -e "\n${YELLOW}Enter the desired branch name for your current branch:${NC}"
    read -r desired_branch
    
    if [[ -z $desired_branch ]]; then
        echo -e "${RED}Branch name cannot be empty.${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Fix branch renaming issue
    echo -e "\n${YELLOW}Fixing branch rename issues...${NC}"
    
    # Rename the local branch if needed
    if [[ $current_branch != $desired_branch ]]; then
        git branch -m $current_branch $desired_branch
        echo -e "${GREEN}Renamed local branch from $current_branch to $desired_branch${NC}"
        current_branch=$desired_branch
    fi
    
    # Check if the branch already exists on remote
    if git ls-remote --heads $remote_name $desired_branch | grep -q $desired_branch; then
        echo -e "${YELLOW}Branch $desired_branch already exists on remote.${NC}"
        echo -e "${YELLOW}Would you like to:${NC}"
        echo "1. Delete remote branch and push local branch"
        echo "2. Force push local branch to remote (overwrite)"
        echo "3. Cancel operation"
        
        read -r remote_choice
        
        case $remote_choice in
            1)
                echo -e "${RED}Deleting remote branch $desired_branch...${NC}"
                git push $remote_name --delete $desired_branch
                echo -e "${GREEN}Pushing local branch to remote...${NC}"
                git push -u $remote_name $desired_branch
                ;;
            2)
                echo -e "${RED}Force pushing to remote branch $desired_branch...${NC}"
                git push -f -u $remote_name $desired_branch
                ;;
            3)
                echo -e "${YELLOW}Operation canceled.${NC}"
                read -p "Press Enter to continue..."
                return
                ;;
            *)
                echo -e "${RED}Invalid option. Operation canceled.${NC}"
                read -p "Press Enter to continue..."
                return
                ;;
        esac
    else
        # Push the branch to remote
        git push -u $remote_name $desired_branch
    fi
    
    echo -e "${GREEN}Branch rename issue fixed. Your branch $desired_branch is now correctly set up.${NC}"
    read -p "Press Enter to continue..."
}

# Function to manage remotes
manage_remotes() {
    echo -e "\n${GREEN}Remote Management:${NC}"
    echo "1. List remotes"
    echo "2. Add remote"
    echo "3. Remove remote"
    echo "4. Change remote URL"
    echo "5. Return to main menu"
    
    read -r remote_choice
    
    case $remote_choice in
        1)
            echo -e "\n${YELLOW}Current remotes:${NC}"
            git remote -v
            ;;
        2)
            echo -e "\n${YELLOW}Enter remote name:${NC}"
            read -r remote_name
            echo -e "${YELLOW}Enter remote URL:${NC}"
            read -r remote_url
            git remote add $remote_name $remote_url
            echo -e "${GREEN}Remote added: $remote_name -> $remote_url${NC}"
            ;;
        3)
            echo -e "\n${YELLOW}Current remotes:${NC}"
            git remote -v
            echo -e "\n${YELLOW}Enter remote name to remove:${NC}"
            read -r remote_remove
            git remote remove $remote_remove
            echo -e "${GREEN}Remote removed: $remote_remove${NC}"
            ;;
        4)
            echo -e "\n${YELLOW}Current remotes:${NC}"
            git remote -v
            echo -e "\n${YELLOW}Enter remote name to change:${NC}"
            read -r remote_change
            echo -e "${YELLOW}Enter new URL:${NC}"
            read -r new_url
            git remote set-url $remote_change $new_url
            echo -e "${GREEN}Remote URL changed for $remote_change -> $new_url${NC}"
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to view logs
view_logs() {
    echo -e "\n${GREEN}Log Options:${NC}"
    echo "1. Show basic log"
    echo "2. Show detailed log"
    echo "3. Show graph log"
    echo "4. Show log for specific branch"
    echo "5. Return to main menu"
    
    read -r log_choice
    
    case $log_choice in
        1)
            git log --oneline -n 10
            ;;
        2)
            git log -n 10
            ;;
        3)
            git log --graph --oneline --all -n 20
            ;;
        4)
            echo -e "\n${YELLOW}Enter branch name:${NC}"
            read -r log_branch
            git log --oneline $log_branch -n 10
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to manage untracked files
manage_untracked() {
    echo -e "\n${GREEN}Manage Untracked Files:${NC}"
    echo "1. List untracked files"
    echo "2. Add all untracked files"
    echo "3. Create/edit .gitignore"
    echo "4. Clean untracked files (BE CAREFUL)"
    echo "5. Return to main menu"
    
    read -r untracked_choice
    
    case $untracked_choice in
        1)
            echo -e "\n${YELLOW}Untracked files:${NC}"
            git ls-files --others --exclude-standard
            ;;
        2)
            git add $(git ls-files --others --exclude-standard)
            echo -e "${GREEN}All untracked files added.${NC}"
            ;;
        3)
            if [[ -f .gitignore ]]; then
                echo -e "${YELLOW}Editing existing .gitignore file${NC}"
            else
                echo -e "${YELLOW}Creating new .gitignore file${NC}"
                # Add some common patterns
                echo "# Automatically generated .gitignore file" > .gitignore
                echo "**/node_modules/" >> .gitignore
                echo "**/__pycache__/" >> .gitignore
                echo "*.log" >> .gitignore
                echo ".DS_Store" >> .gitignore
                echo ".env" >> .gitignore
                echo "*.pyc" >> .gitignore
            fi
            
            echo -e "${YELLOW}Enter your preferred editor (default: nano):${NC}"
            read -r editor
            
            if [[ -z $editor ]]; then
                editor="nano"
            fi
            
            $editor .gitignore
            echo -e "${GREEN}.gitignore file updated.${NC}"
            ;;
        4)
            echo -e "${RED}WARNING: This will delete all untracked files. This action cannot be undone.${NC}"
            echo -e "${RED}Are you absolutely sure? (type 'YES' to confirm)${NC}"
            read -r confirm_clean
            
            if [[ $confirm_clean == "YES" ]]; then
                git clean -fd
                echo -e "${GREEN}Untracked files cleaned.${NC}"
            else
                echo -e "${YELLOW}Clean operation canceled.${NC}"
            fi
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to merge branches
merge_branches() {
    echo -e "\n${GREEN}Merge Branches:${NC}"
    
    # Show available branches
    echo -e "${YELLOW}Available branches:${NC}"
    git branch
    
    # Get current branch
    current_branch=$(git branch --show-current)
    echo -e "\n${YELLOW}Current branch: $current_branch${NC}"
    
    # Get source branch
    echo -e "\n${YELLOW}Enter the branch you want to merge FROM:${NC}"
    read -r source_branch
    
    # Verify source branch exists
    if ! git show-ref --verify --quiet refs/heads/$source_branch; then
        echo -e "${RED}Error: Branch '$source_branch' does not exist.${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Confirm merge
    echo -e "${YELLOW}You are about to merge $source_branch INTO $current_branch.${NC}"
    echo -e "${YELLOW}Continue with merge? (y/n)${NC}"
    read -r confirm_merge
    
    if [[ $confirm_merge != "y" && $confirm_merge != "Y" ]]; then
        echo -e "${YELLOW}Merge canceled.${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Ask for merge strategy
    echo -e "\n${YELLOW}Select merge strategy:${NC}"
    echo "1. Regular merge (creates merge commit)"
    echo "2. Fast-forward merge (if possible)"
    echo "3. Squash merge (combines all commits into one)"
    echo "4. Rebase (replays commits on top of target branch)"
    read -r merge_strategy
    
    # Perform merge based on selected strategy
    case $merge_strategy in
        1)
            echo -e "${YELLOW}Performing regular merge...${NC}"
            git merge $source_branch
            ;;
        2)
            echo -e "${YELLOW}Attempting fast-forward merge...${NC}"
            git merge --ff-only $source_branch
            if [ $? -ne 0 ]; then
                echo -e "${RED}Fast-forward merge not possible.${NC}"
                echo -e "${YELLOW}Would you like to do a regular merge instead? (y/n)${NC}"
                read -r do_regular
                if [[ $do_regular == "y" || $do_regular == "Y" ]]; then
                    git merge $source_branch
                else
                    echo -e "${YELLOW}Merge canceled.${NC}"
                fi
            fi
            ;;
        3)
            echo -e "${YELLOW}Performing squash merge...${NC}"
            git merge --squash $source_branch
            echo -e "${YELLOW}Changes have been staged. You need to commit them.${NC}"
            echo -e "${YELLOW}Do you want to commit now? (y/n)${NC}"
            read -r commit_now
            if [[ $commit_now == "y" || $commit_now == "Y" ]]; then
                echo -e "${YELLOW}Enter commit message for the squash merge:${NC}"
                read -r squash_message
                git commit -m "$squash_message"
                echo -e "${GREEN}Squash merge completed and committed.${NC}"
            else
                echo -e "${YELLOW}Squash merge changes staged but not committed.${NC}"
            fi
            ;;
        4)
            echo -e "${YELLOW}Performing rebase...${NC}"
            git rebase $source_branch
            ;;
        *)
            echo -e "${RED}Invalid option. Merge canceled.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to manage tags
manage_tags() {
    echo -e "\n${GREEN}Manage Tags:${NC}"
    echo "1. List all tags"
    echo "2. Create a new tag"
    echo "3. Delete a tag"
    echo "4. Push tags to remote"
    echo "5. Return to main menu"
    
    read -r tag_choice
    
    case $tag_choice in
        1)
            echo -e "\n${YELLOW}Current tags:${NC}"
            git tag -n  # Shows tags with annotations
            ;;
        2)
            echo -e "\n${YELLOW}Enter tag version (e.g., v1.0.0):${NC}"
            read -r tag_version
            
            echo -e "${YELLOW}Tag a specific commit? (y/n)${NC}"
            read -r specific_commit
            
            if [[ $specific_commit == "y" || $specific_commit == "Y" ]]; then
                echo -e "${YELLOW}Recent commits:${NC}"
                git log --oneline -n 10
                
                echo -e "\n${YELLOW}Enter commit hash to tag:${NC}"
                read -r commit_hash
                
                echo -e "${YELLOW}Enter tag message (optional):${NC}"
                read -r tag_message
                
                if [[ -z $tag_message ]]; then
                    git tag $tag_version $commit_hash
                else
                    git tag -a $tag_version -m "$tag_message" $commit_hash
                fi
            else
                echo -e "${YELLOW}Enter tag message (optional):${NC}"
                read -r tag_message
                
                if [[ -z $tag_message ]]; then
                    git tag $tag_version
                else
                    git tag -a $tag_version -m "$tag_message"
                fi
            fi
            
            echo -e "${GREEN}Tag created: $tag_version${NC}"
            ;;
        3)
            echo -e "\n${YELLOW}Current tags:${NC}"
            git tag
            
            echo -e "\n${YELLOW}Enter tag to delete:${NC}"
            read -r del_tag
            
            echo -e "${RED}Are you sure you want to delete tag $del_tag? (y/n)${NC}"
            read -r confirm_delete
            
            if [[ $confirm_delete == "y" || $confirm_delete == "Y" ]]; then
                git tag -d $del_tag
                echo -e "${GREEN}Local tag deleted: $del_tag${NC}"
                
                echo -e "${YELLOW}Delete this tag from remote as well? (y/n)${NC}"
                read -r delete_remote
                
                if [[ $delete_remote == "y" || $delete_remote == "Y" ]]; then
                    echo -e "${YELLOW}Enter remote name (default: origin):${NC}"
                    read -r remote_name
                    
                    if [[ -z $remote_name ]]; then
                        remote_name="origin"
                    fi
                    
                    git push $remote_name --delete refs/tags/$del_tag
                    echo -e "${GREEN}Remote tag deleted from $remote_name: $del_tag${NC}"
                fi
            else
                echo -e "${YELLOW}Tag deletion canceled.${NC}"
            fi
            ;;
        4)
            echo -e "\n${YELLOW}Enter remote name (default: origin):${NC}"
            read -r remote_name
            
            if [[ -z $remote_name ]]; then
                remote_name="origin"
            fi
            
            echo -e "${YELLOW}Push all tags or a specific tag?${NC}"
            echo "1. Push all tags"
            echo "2. Push a specific tag"
            read -r push_choice
            
            if [[ $push_choice == "1" ]]; then
                git push $remote_name --tags
                echo -e "${GREEN}All tags pushed to $remote_name.${NC}"
            elif [[ $push_choice == "2" ]]; then
                echo -e "\n${YELLOW}Current tags:${NC}"
                git tag
                
                echo -e "\n${YELLOW}Enter tag to push:${NC}"
                read -r push_tag
                
                git push $remote_name refs/tags/$push_tag
                echo -e "${GREEN}Tag $push_tag pushed to $remote_name.${NC}"
            else
                echo -e "${RED}Invalid option. Push canceled.${NC}"
            fi
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

# Main function
main() {
    if ! check_git_repo; then
        exit 1
    fi
    
    while true; do
        display_header
        display_menu
        
        read -r choice
        
        case $choice in
            1)
                git_status
                ;;
            2)
                commit_changes
                ;;
            3)
                push_changes
                ;;
            4)
                pull_changes
                ;;
            5)
                branch_management
                ;;
            6)
                fix_branch_rename_issues
                ;;
            7)
                merge_branches
                ;;
            8)
                manage_tags
                ;;
            9)
                manage_remotes
                ;;
            10)
                view_logs
                ;;
            11)
                manage_untracked
                ;;
            0)
                echo -e "${GREEN}Exiting Git Repository Manager. Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please try again.${NC}"
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Run the main function
main
