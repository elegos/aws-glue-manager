# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.0.5] - 2021-06-04
- AppImage build via AppDirBuilder + appimagetool
- Do not block the entire tab view when updating the jobs, but only the action buttons
- Workflows tab:
  - list of workflows
  - filter by name, last execution status
  - configurable status icon logic via checkbox

## [v0.0.4.1] - 2021-03-31
### Changed
- Improved jobs chart loading times

## [v0.0.4] - 2021-03-31
### Added
- Last 24 hours Glue usage chart (jobs tab)
  - Concurrent DPU usage
  - Concurrent number of active jobs


## [v0.0.3] - 2021-03-30
### Changed
- Fixed: show the wrong job details when double clicking on the filtered jobs list (jobs tab)
- Fixed: do not update / show the correct jobs in the jobs list when the refresh action is requested (jobs tab)
