# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test audit RBAC"""

import itertools

from os.path import abspath
from os.path import dirname
from os.path import join
from collections import defaultdict
from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
import json

import integration.ggrc.generator

from ggrc import db
from ggrc.models import all_models
from integration.ggrc_basic_permissions.models \
  import factories as rbac_factories
from integration.ggrc.models import factories


DEFAULT_LACK_OF_PERMISSIONS = {
    "Snapshot": 403,
    "Audit": 403
}
DEFAULT_AUDITOR_PERMISSIONS = {
    "Snapshot": 200,
    "Audit": 403
}


class TestAuditRBAC(TestCase):
  """Test audit RBAC"""
  # pylint: disable=too-many-instance-attributes

  CSV_DIR = join(abspath(dirname(__file__)), "test_csvs")
  @staticmethod
  def build_relationship_json(source, destination, is_external=False):
    """Builds relationship create request json."""
    return json.dumps([{
      "relationship": {
        "source": {"id": source.id, "type": source.type},
        "destination": {"id": destination.id, "type": destination.type},
        "context": {"id": None},
        "is_external": is_external
      }
    }])

  def setUp(self):
    """Imports test_csvs/audit_rbac_snapshot_create.csv needed by the tests"""
    TestCase.clear_data()
    self.api = Api()
    # import ipdb
    # ipdb.set_trace()
    self.objgen = integration.ggrc.generator.ObjectGenerator()

    self.create_users()
    self.assign_roles()

    self.people = all_models.Person.eager_query().all()

    self.auditor_role = all_models.AccessControlRole.query.filter(
        all_models.AccessControlRole.name == "Auditors"
    ).one()

    program = factories.ProgramFactory()

    self.program = db.session.query(all_models.Program).filter(
        all_models.Program.title == program.title
    ).one()

    access = factories.AccessGroupFactory()
    ag = all_models.AccessGroup.query.filter(
      all_models.AccessGroup.title == access.title).one()

    self.HEADERS = {
      "Content-Type": "application/json",
      "X-requested-by": "External App",
      "X-ggrc-user": "{\"email\": \"external_app@example.com\"}",
      "X-appengine-inbound-appid": "test_external_app",
    }
    self.REL_URL = "/api/relationships"

    with factories.single_commit():
      program = factories.ProgramFactory()
      access = factories.AccessGroupFactory()
      response = self.api.client.post(
        self.REL_URL,
        data=self.build_relationship_json(program, access, True),
        headers=self.HEADERS)
      self.assert200(response)

    factories.RelationShipFactory(source=ag, destination=program)

    sources = set(r.source for r in self.program.related_sources)
    destinations = set(r.destination
                       for r in self.program.related_destinations)
    related = [obj for obj in sources.union(destinations)
               if not isinstance(obj, all_models.Person)]
    self.related_objects = related

    self.api = Api()
    self.client.get("/login")

    self.audit = self.create_audit()

    self.snapshots = all_models.Snapshot.eager_query().all()


  def create_users(self):
    """Create users for RBAC tests"""
    #self.testuser = factories.PersonFactory(email="user@example.com")
    self.admin = factories.PersonFactory(email="admin@test.com")
    self.creatorpm = factories.PersonFactory(email="creatorpm@test.com")
    self.creator = factories.PersonFactory(email="creator@test.com")
    self.readerpm = factories.PersonFactory(email="readerpm@test.com")
    self.reader = factories.PersonFactory(email="reader@test.com")
    self.editorpm = factories.PersonFactory(email="editorpm@test.com")
    self.editor = factories.PersonFactory(email="editor@test.com")
    self.adminpm = factories.PersonFactory(email="adminpm@test.com")
    self.creatorpr = factories.PersonFactory(email="creatorpr@test.com")
    self.readerpr = factories.PersonFactory(email="readerpr@test.com")
    self.editorpr = factories.PersonFactory(email="editorpr@test.com")
    self.adminpr = factories.PersonFactory(email="adminpr@test.com")
    self.creatorpe = factories.PersonFactory(email="creatorpe@test.com")
    self.readerpe = factories.PersonFactory(email="readerpe@test.com")
    self.editorpe = factories.PersonFactory(email="editorpe@test.com")
    self.adminpe = factories.PersonFactory(email="adminpe@test.com")
    self.readerauditor = factories.PersonFactory(email="readerauditor@test.com")
    self.creatorauditor = factories.\
      PersonFactory(email="creatorauditor@test.com")
    self.editorauditor = factories.PersonFactory(email="editorauditor@test.com")
    self.adminauditor = factories.PersonFactory(email="adminauditor@test.com")

    self.admins = [self.admin, self.adminpm, self.adminpr, self.adminpe,
                    self.adminauditor]
    self.creators = [self.creator, self.creatorpm, self.creatorpr,
                     self.creatorpe, self.creatorauditor]
    self.editors = [self.editor, self.editorpm, self.editorpr, self.editorpe,
                    self.editorauditor]
    self.readers = [self.reader, self.readerpm, self.readerpr, self.readerpe,
                    self.readerauditor]

  def assign_role_to_users(self, rolename, users):
    """Assign roles"""
    role = all_models.Role.query.filter(
      all_models.Role.name == rolename).one()
    for user in users:
      rbac_factories.UserRoleFactory(role=role,
                                     person=user)

  def assign_roles(self):
    """Assign roles to the user created"""
    self.assign_role_to_users('Administrator', self.admins)
    self.assign_role_to_users('Creator', self.creators)
    self.assign_role_to_users('Editor', self.editors)
    self.assign_role_to_users('Reader', self.readers)


  def create_audit(self):
    """Create default audit for audit snapshot RBAC tests"""
    self.people = all_models.Person.eager_query().all()
    people = {person.email: person for person in self.people}
    # people = {person.email: person for person in self.person}

    auditor_emails = [
        "readerauditor@test.com",
        "creatorauditor@test.com",
        "editorauditor@test.com",
        "adminauditor@test.com",
    ]
    _, audit = self.objgen.generate_object(all_models.Audit, {
        "title": "Snapshotable audit",
        "program": {"id": self.program.id},
        "status": "Planned",
        "snapshots": {
            "operation": "create",
        },
        "access_control_list": [{
            "ac_role_id": self.auditor_role.id,
            "person": {
                "id": people[person].id,
                "type": "Person"
            }
        } for person in auditor_emails],
        "context": {
            "type": "Context",
            "id": self.program.context_id,
            "href": "/api/contexts/{}".format(self.program.context_id)
        }
    })
    return audit

  def update_audit(self):
    """Update default audit"""
    #self.import_file(next(self.csv_files))

    audit = all_models.Audit.query.filter(
        all_models.Audit.title == "Snapshotable audit"
    ).one()
    self.audit = audit

    self.api.modify_object(self.audit, {
        "snapshots": {
            "operation": "upsert"
        }
    })

  def read(self, objects):
    """Attempt to do a GET request for every object in the objects list"""
    responses = []
    for obj in objects:
      status_code = self.api.get(obj.__class__, obj.id).status_code
      responses.append((obj.type, status_code))
    return responses

  def update(self, objects):
    """Attempt to do a PUT request for every object in the objects list"""
    scope_response = self.api.get(self.audit.__class__, self.audit.id)
    if scope_response.status_code == 200:
      self.update_audit()

    responses = []
    for obj in objects:
      response = self.api.get(obj.__class__, obj.id)
      status_code = response.status_code
      if response.status_code == 200:
        data = response.json
        if obj.type == "Snapshot":
          data.update({
              "update_revision": "latest"
          })
        put_call = self.api.put(obj, data)
        status_code = put_call.status_code
      responses.append((obj.type, status_code))
    return responses

  def call_api(self, method, expected_statuses):
    """Calls the REST api with a given method and returns a list of
       status_codes that do not match the expected_statuses dict"""
    all_errors = []
    for person in self.people:
      self.api.set_user(person)
      responses = method(self.snapshots + [self.audit])
      for type_, code in responses:
        if code != expected_statuses[person.email][type_]:
          all_errors.append("{} does not have {} access to {} ({})".format(
              person.email, method.__name__, type_, code))
    return all_errors

  def test_read_access_on_mapped(self):
    """Test READ access to snapshotted objects of default audit"""
    expected_statuses = defaultdict(lambda: defaultdict(lambda: 200))
    exceptional_users = (
        ("creator@test.com", DEFAULT_LACK_OF_PERMISSIONS),
    )
    for user, exceptions in exceptional_users:
      for type_, status_code in exceptions.items():
        expected_statuses[user][type_] = status_code
    errors = self.call_api(self.read, expected_statuses)
    assert not errors, "\n".join(errors)

  # def test_update_access_on_mapped(self):
  #   """Test UPDATE access to snapshotted objects of default audit"""
  #   print "In test_update_access_on_mapped"
  #   expected_statuses = defaultdict(lambda: defaultdict(lambda: 200))
  #
  #   exceptional_users = (
  #       ("creator@test.com", DEFAULT_LACK_OF_PERMISSIONS),
  #       ("reader@test.com", DEFAULT_LACK_OF_PERMISSIONS),
  #       ("creatorpr@test.com", DEFAULT_LACK_OF_PERMISSIONS),
  #       ("readerpr@test.com", DEFAULT_LACK_OF_PERMISSIONS),
  #       # Auditor roles
  #       ("readerauditor@test.com", DEFAULT_AUDITOR_PERMISSIONS),
  #       ("creatorauditor@test.com", DEFAULT_AUDITOR_PERMISSIONS)
  #   )
  #
  #   for user, exceptions in exceptional_users:
  #     for type_, status_code in exceptions.items():
  #       expected_statuses[user][type_] = status_code
  #
  #   errors = self.call_api(self.update, expected_statuses)
  #   assert not errors, "\n".join(errors)
