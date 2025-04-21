# OpenSim Resource Exploration Notes

## Main Resources Identified

### Documentation
- **Main Documentation**: https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/overview
  - User's Guide
  - API Documentation
  - Examples and Tutorials
  - Troubleshooting
  - Models, Data, & Utilities

### GitHub Repositories
- **Main Repository**: https://github.com/opensim-org/opensim-core
  - Contains C++ libraries, command-line applications, and Java/Python bindings
  - Does not include GUI source code (separate repository)

### API Documentation
- **API Docs**: https://simtk.org/api_docs/opensim/api_docs/
  - Detailed class documentation
  - Hierarchical structure of OpenSim components

### Website
- **Main Website**: https://opensim.stanford.edu/
  - Overview of OpenSim capabilities
  - Links to documentation and resources
  - Information about the OpenSim ecosystem

### SimTK Project Page
- **Project Page**: https://simtk.org/projects/opensim
  - Downloads
  - Forums
  - Source code links

## Key Documentation Areas for Scraping

1. **User's Guide** - Contains detailed information about using OpenSim
2. **API Documentation** - Technical details about OpenSim classes and methods
3. **Examples and Tutorials** - Practical usage examples
4. **GitHub README and Wiki** - Installation and development information
5. **Forum Discussions** - Common questions and answers

## Scraping Strategy

1. Use web scraping for the documentation pages on Confluence
2. Use GitHub API to access repository content
3. Scrape API documentation for technical details
4. Collect open access papers from Google Scholar

## Next Steps

1. Set up development environment with necessary libraries
2. Implement scrapers for each identified resource
3. Process and prepare the collected data for the RAG system
