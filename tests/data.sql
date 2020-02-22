-- Generate passwords with werkzeug.security.generate_password_hash("testpassword")
INSERT INTO users (id, login, name, admin, password) VALUES ('admin1', 'admin1', 'Test Admin 1', true,
  'pbkdf2:sha256:150000$mL1FDhtT$2532b49ae948bdc19c3d25d60fca15a32830db2f88ab2e52cbd4f8b5e236ce44');
INSERT INTO users (id, login, name, password) VALUES ('user1', 'user1', 'Test User 1',
  'pbkdf2:sha256:150000$vHHTmybn$3be07075130c459d3f2b8f29253fa5a473f74ee2be8e0f4ea0547ddab95e645f');
-- prepopulated test project with allocation for submission
INSERT INTO users (id, login, name, password) VALUES ('pi1', 'pi1', 'Test PI 1',
  'pbkdf2:sha256:150000$AgdLhY6N$7a9f2df5f0387455a6a9285f13736d266c383f0f7b21eb510c3ad1a0e950161b');
INSERT INTO allocations (id, project_id, submitter_id, state, cloud_id) VALUES ('testalloc1', 'def-pi1-ac', 'tst-002', 'Submitted', 'devstack');
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc1', 'vcpus', 4);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc1', 'memgb', 16);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc1', 'vols', 8);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc1', 'volgb', 64);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc1', 'fips', 2);
-- "active" allocation to adjust
INSERT INTO allocations (id, project_id, submitter_id, state, cloud_id) VALUES ('testalloc2', 'def-pi1-ac', 'tst-002', 'Active', 'arbutus');
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc2', 'vcpus', 4);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc2', 'memgb', 16);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc2', 'vols', 8);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc2', 'volgb', 64);
INSERT INTO quotas (allocation_id, resource, quota) VALUES ('testalloc2', 'fips', 2);
-- prepopulated test ACL to verify updates
INSERT INTO acls (id, project_id, cloud_id, submitter_id, state) VALUES ('testacl1', 'def-pi1-ab', 'devstack', 'testpi', 'Draft');
INSERT INTO rules (acl_id, user_id, access) VALUES ('testacl1', 'testpi', 'Assigned');
-- prepopulated test ACLs to verify difference calculation
INSERT INTO acls (id, project_id, cloud_id, submitter_id, state) VALUES ('testacl1D', 'def-pi1-ac', 'testcloud', 'nobody', 'Draft');
INSERT INTO acls (id, project_id, cloud_id, submitter_id, state) VALUES ('testacl1A', 'def-pi1-ac', 'testcloud', 'nobody', 'Active');
INSERT INTO rules (acl_id, user_id, access) VALUES ('testacl1D', 'testpi', 'assigned');
INSERT INTO rules (acl_id, user_id, access) VALUES ('testacl1D', 'testu1', 'unassigned');
INSERT INTO rules (acl_id, user_id, access) VALUES ('testacl1D', 'testu2', 'assigned');
INSERT INTO rules (acl_id, user_id, access) VALUES ('testacl1A', 'testpi', 'assigned');
INSERT INTO rules (acl_id, user_id, access) VALUES ('testacl1A', 'testu1', 'assigned');
INSERT INTO rules (acl_id, user_id, access) VALUES ('testacl1A', 'testu2', 'unassigned');
