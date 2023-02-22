# Weekly assingment

Tasks done in the first during the course.

## Samuli

### Week 1

As a team we did the first assingment filling the user-stories and stakeholder
analysysis and did the OWASP considerations.

I forked and created teams project from the courses repo and made
this `md` template for the answers. I also set up the local development environment.

### Week 2

Changed reporting template.

Configured mongoDB to work in my local container.

Made and assinged issues from user cases.

Made development branch.


### Week 4

Add non-funtional requirements as issues to the project. Edit existing issues and further specify functional requirements. 

Started working on the final project and presentation


### Week 5

Finalizing the program and made the final report and presentation materials. 

## Ville

##WEEK 1:
Helped with the stakeholder analysis, environment setup etc
##Week 2:
Fixed Gitlab runners picking wrong branches, fixed MongoDb config to use correct database. Setup mongodb to work in actual production (Azure side stuff)
##WEEK 3:
Helped with password security (hashing and salting), changed gitlab runners to pick correct tags, so developement branch wasn't the production version
##WEEK 4:
- Added password checks
- Added min and max age requirements
- Added ability to store, update and delete items to/from backend, some css fixes
##WEEK 5:
- Fixed bidding error if there is no bidding history
- Fixed crash on empty bid value, added required tags for important fields
- Added email validation
- Fixed tailwind support
- Added testing, coverage, static security testing, fixed staging not working -> made pipeline work correctly
- Made sentry logging to work in production
- Added terms and agreements popup
- Added min and max length requirements to some fields. Fixed login crash, set user to None by default
- Made mongodb to use its test database when running tests
- Disable debug mode when running tests
- Added pem for git ignore
- Enabled password checks and made some final minute translations

## Linda

### Week 1

Participated in making of the stakeholder cards and user stories.

Started to set up my local development environment.

### Week 2

Set up Azure environment (resource group, container registry, deployment target) and pipeline. Finished the local development environment.

### Week 3

Configured mongoDB to work in my local container.

Added user registeration, login and logout functionalities to site. Also made the base.html template and other required templates. Added css files and made UI look better.

Started to set up logging and monitoring.

### Week 4

### Week 5

## Ari

### Week 1

Set some ground rules for the team and did some basic recon on what kind of roles we should expect

Made stakeholder cards as a group

setup the dev environment and made sure everything works
### Week 2

Added basic functionality for mongodb

### Week 3

Helped Linda and Ville for configuring mongo, and login functionalities. Did some research on OWASP considerations and how to implement those in our program 

### Week 4
Finished setting up logging. Opened account at sentry.io and listed our project there

### Week 5
Added support for currency conversion and localization. Users can now choose between finnish and english language.
Added finnish translation of the website. 
Wrote tests for all of these functionalities and made sure they work.


-------------------------------
## OWASP considerations

As a team, we have decided that the OWASP security consideration examples that
are most appicaple are:

- Input validation: With proper input validation,
- Authentication and access controls,
- Logging and monitoring,
- Vulnerabilities management,
- Least privilege.

With input validation, you are able to detect and prevent malicious or
unintended data from system user from being entered into the system.

Implementing authentication and access control is crucial in maintaining
security of a system as it ensures that authorized individuals are granted
access to the system and it's information.

Logging and monitoring are important as they enable tracking of system activity.
This allows for prompt detection and response to security breaches.

Vulnerability management helps developers to identify and assess vulnerabilities
in their systems and take appropriate actions to eliminate them.

System developlent using least privilege principle limits access to system resources
and functionalities to only essential users.
