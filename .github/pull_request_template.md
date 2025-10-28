### Changelog
Paste the changelog here. 

### Linked issues
Link the issues solved by this PR like below:

Closes: #0  <!-- Replace 0 by issue number -->

### Integration tests
Test if the proposed change does not break the pipeline or API:

- [ ] The proposed change works locally
- [ ] The proposed change is deployed to test and works as expected:
  - [ ] The test pipeline successfully retrieves data from dataplatform
  - [ ] The test API successfully receives data from the test pipeline and processes the data
  - [ ] The test API successfully writes the data to the test database
- [ ] The dashboard(s) work after the proposed change

Link to the test API: https://rsc.ds.umcutrecht.nl/content/d1913575-7d86-4bbd-9229-48db1ba3ae96/
Link to the test dashboard: https://rsc.ds.umcutrecht.nl/connect/#/apps/a4f403a9-8d43-4757-8caf-c78fb0669dfc
Link to the test pipeline: https://cogstack-acc.ds.umcutrecht.nl/nifi/?processGroupId=e579d736-018d-1000-5887-973968ac645c&componentIds=