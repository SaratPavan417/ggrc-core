# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Fix foreign keys in DB

Create Date: 2019-07-23 09:41:45.159838
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = 'cd25eeaf8175'
down_revision = 'ac75e70c9081'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute("""
    ALTER TABLE `audits` ADD CONSTRAINT `audit_firm_id`
    FOREIGN KEY (`audit_firm_id`)
    REFERENCES `org_groups` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `contexts` ADD CONSTRAINT `context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `custom_attribute_definitions` ADD CONSTRAINT
    `fk_custom_attribute_definitions_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `custom_attribute_values` ADD CONSTRAINT
    `fk_custom_attribute_values_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `cycle_task_groups` ADD CONSTRAINT
    `secondary_contact_id`
    FOREIGN KEY (`secondary_contact_id`)
    REFERENCES `people` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `cycle_task_groups` ADD CONSTRAINT
    `task_group_id`
    FOREIGN KEY (`task_group_id`)
    REFERENCES `task_groups` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `cycles` ADD CONSTRAINT
    `fk_cycles_secondary_contact_id`
    FOREIGN KEY (`secondary_contact_id`)
    REFERENCES `people` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `notification_types` ADD CONSTRAINT
    `fk_notification_types_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `notifications` ADD CONSTRAINT
    `fk_notifications_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `notifications_history` ADD CONSTRAINT
    `fk_notifications_history_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE
    """)
  op.execute("""
    ALTER TABLE `risk_assessments` ADD CONSTRAINT
    `program_id`
    FOREIGN KEY (`program_id`)
    REFERENCES `programs` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `roles` ADD CONSTRAINT
    `fk_roles_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `saved_searches` ADD CONSTRAINT
    `person_id`
    FOREIGN KEY (`person_id`)
    REFERENCES `people` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `snapshots` ADD CONSTRAINT
    `fk_snapshots_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `task_groups` ADD CONSTRAINT
    `fk_task_groups_secondary_contact_id`
    FOREIGN KEY (`secondary_contact_id`)
    REFERENCES `people` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `threats` ADD CONSTRAINT
    `fk_threats_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `user_roles` ADD CONSTRAINT
    `fk_user_roles_person_id`
    FOREIGN KEY (`person_id`)
    REFERENCES `people` (`id`)
    ON DELETE CASCADE""")
  op.execute("""
    ALTER TABLE `vendors` ADD CONSTRAINT
    `fk_vendors_context_id`
    FOREIGN KEY (`context_id`)
    REFERENCES `contexts` (`id`)
    ON DELETE CASCADE""")


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  raise NotImplementedError("Downgrade is not supported")
