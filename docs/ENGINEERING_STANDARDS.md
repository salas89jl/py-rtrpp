This document serves as a comprehensive guide to the engineering standards and best practices followed in the Real-Time Robotics Perception Platform (RTRPP) project. It outlines the coding conventions, documentation guidelines, version control practices, and other essential standards that ensure the maintainability, scalability, and quality of the codebase.



## Workflow and Version Control

This workflow establishes a consistent Git development process for the RTRPP project. It is intended to maintain a stable production branch while allowing new features, experiments, and bug fixes to be developed in parallel. The workflow is designed to be simple and easy to follow, while also providing a clear structure for managing code changes. Although, this workflow is designed to be maintained by a single developer, it can be easily adapted for a team of developers.

## Git Branching Strategy
```text
main 
    Stable working branch. All production-ready code is merged into this branch.
dev
    Development branch. All new features and bug fixes are merged into this branch.

feature/<feature-name>
    Branch for developing a new feature. Created from the dev branch. Once the feature is completed and tested, it is merged back into the dev branch.
```

## Normal work procedure (No pull request required; solo work)
1. Create a new branch from the `dev` branch for your feature or bug fix.
```text
git checkout dev
git checkout -b feature/<feature-name>
```
2. Run the pipeline to ensure that the code is working as expected.
3. Make your changes and test them locally.
4. Verify that the changes do not break any existing functionality by running the test suite.
5. After completing the changes, commit your changes and push the branch to the remote repository.
```text
git add .
git commit -m "Add <feature-name>"
git push origin feature/<feature-name>
```
6. Merge the feature branch back into the `dev` branch.
```text
git checkout dev
git merge feature/<feature-name>
git push origin dev
```
7. Delete the feature branch from the remote repository.
```text
git push origin --delete feature/<feature-name>
```
8. If the changes are ready for production, merge the `dev` branch into the `main` branch.
```text
git checkout main
git merge dev
git tag -a v<version-number> -m "Release version <version-number>"
git push origin main --tags
```


Helpful Notes:
- Always ensure that you are working on the latest version of the `dev` branch before creating a new feature branch. You can do this by running `git pull origin dev` before creating a new branch.
- Use descriptive names for your feature branches to make it clear what the branch is for. For example, use `feature/login-system` instead of `feature/feature1`.
- Regularly run the test suite to catch any issues early in the development process. This will help ensure that your changes do not introduce new bugs or break existing functionality.
- Keep feature branches local until the feature is complete and tested. This will help prevent incomplete or unstable code from being merged into the `dev` branch.

- When merging feature branches back into the `dev` branch, resolve any merge conflicts that may arise. This may require manual intervention to ensure that the code is merged correctly and that no functionality is lost.
- Before merging the `dev` branch into the `main` branch, ensure that all changes have been thoroughly tested and reviewed. This will help maintain the stability of the production code and prevent any issues from being introduced into the main branch.

## Changelog
When making changes to the codebase, it is important to maintain a clear and concise changelog. This will help keep track of what changes have been made, when they were made, and who made them. The changelog should be updated with each new release and should include the following information:
- Version number
- Date of release
- Added features
- Changed features
- Fixed bugs

### Example Changelog Entry
```text
## [1.0.0] - 2024-06-01

### Added
- Initial release of the RTRPP project.

### Changed
- N/A

### Fixed
- N/A
```

Add ENGINEERING_STANDARDS with version control practices