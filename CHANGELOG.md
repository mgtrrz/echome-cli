# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Types of changes:

* Added
* Changed
* Deprecated
* Removed
* Fixed
* Security

## [Unreleased]

## [0.3.2] - 2022-01-25

### Fixed
- Script should now properly install

## [0.3.1] - 2022-01-25

### Fixed
- Issue with Python imports

## [0.3.0] - 2022-01-25

### Added
- Support for new endpoints with updated python-sdk library
- Some commands now have an extra flag for producing wider table output with more information

### Changed
- Help/Usage output is more consolidated and easier to read
- Consolidated commands to match the endpoints
- The format argument (--format, -f) has been changed to --output, -o. The options have stayed the same
- Better Kubernetes support
- Uses latest version of ecHome Python SDK

## [0.2.0] - 2021-04-03

### Fixed 
- Additional arguments for registering images


### Changed
- Allows vm create to use new VirtualNetwork profile 

## [0.1.1] - 2020-08-16

### Changed
- Allows vm create to use new VirtualNetwork profile 

## [0.1.0] - 2020-07-01

### Added
- Initial import of ecHome CLI

[unreleased]: https://github.com/mgtrrz/echome-cli/compare/0.3.2...HEAD
[0.3.2]: https://github.com/mgtrrz/echome-cli/compare/0.3.1...0.3.2
[0.3.1]: https://github.com/mgtrrz/echome-cli/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/mgtrrz/echome-cli/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/mgtrrz/echome-cli/compare/0.1.0...0.2.0
[0.1.1]: https://github.com/mgtrrz/echome-cli/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/mgtrrz/echome-cli/releases/tag/0.1.0
