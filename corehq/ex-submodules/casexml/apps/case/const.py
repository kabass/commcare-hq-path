# how cases/referrals are tagged in the xform/couch

from datetime import timedelta

CASE_TAG = "case"
REFERRAL_TAG = "referral"

# internal case identifiers
CASE_ACTION_INDEX = "index"
CASE_ACTION_CREATE = "create"
CASE_ACTION_UPDATE = "update"
CASE_ACTION_CLOSE = "close"
CASE_ACTION_ATTACHMENT = "attachment"
CASE_ACTION_COMMTRACK = "commtrack"
CASE_ACTION_REBUILD = "rebuild"
CASE_ACTIONS = (
    CASE_ACTION_CREATE, CASE_ACTION_UPDATE, CASE_ACTION_INDEX, CASE_ACTION_CLOSE,
    CASE_ACTION_ATTACHMENT, CASE_ACTION_COMMTRACK, CASE_ACTION_REBUILD,
)

# this might not be used / be combined with close, but for now consider it different
CASE_ACTION_PURGE = "purge"

CASE_TAG_TYPE = "case_type"
CASE_TAG_TYPE_ID = "case_type_id"
CASE_TAG_ID = "case_id"
CASE_ATTR_ID = "@case_id"
CASE_TAG_NAME = "case_name"
CASE_TAG_MODIFIED = "date_modified"
CASE_TAG_USER_ID = "user_id"
CASE_TAG_EXTERNAL_ID = "external_id"
CASE_TAG_DATE_OPENED = "date_opened"
CASE_TAG_OWNER_ID = "owner_id"
XMLNS = "@xmlns"


CASE_TAGS = (CASE_ACTION_CREATE, CASE_ACTION_UPDATE, CASE_ACTION_CLOSE, CASE_ACTION_ATTACHMENT, REFERRAL_TAG,
             CASE_TAG_TYPE_ID, CASE_TAG_ID, CASE_TAG_NAME, CASE_TAG_MODIFIED, CASE_TAG_USER_ID,
             CASE_TAG_EXTERNAL_ID, CASE_TAG_DATE_OPENED)

RESTRICTED_PROPERTIES = (CASE_TAG_ID, CASE_ATTR_ID, CASE_TAG_MODIFIED,
                         CASE_TAG_TYPE, CASE_TAG_NAME, CASE_TAG_DATE_OPENED, XMLNS)

CASE_INDEX_EXTENSION = 'extension'
CASE_INDEX_CHILD = 'child'
CASE_INDEX_IDENTIFIER_PARENT = 'parent'
CASE_INDEX_IDENTIFIER_HOST = 'host'

DEFAULT_CASE_INDEX_IDENTIFIERS = {
    CASE_INDEX_CHILD: CASE_INDEX_IDENTIFIER_PARENT,
    CASE_INDEX_EXTENSION: CASE_INDEX_IDENTIFIER_HOST
}

UNOWNED_EXTENSION_OWNER_ID = '-'

ARCHIVED_CASE_OWNER_ID = '_archive_'

SIGNIFICANT_TIME = timedelta(hours=12)
