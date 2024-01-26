from ariadne import MutationType, ObjectType, QueryType, SubscriptionType
from krispcall.campaigns.entrypoints.graphql.resolvers.mutation import (
    resolve_add_campaign_call_note,
    resolve_add_campaign_callscripts,
    resolve_add_campaign_contact_detail,
    resolve_add_campaign_voicemail,
    resolve_campaign_voicemail_drop,
    resolve_create_contact_list_with_csv,
    resolve_delete_campaign_contact_detail,
    resolve_update_campaign_call_note,
    resolve_update_campaign_callscripts,
    resolve_update_campaign_contact_list,
    resolve_update_campaign_voicemail,
    resolve_upload_contact_detail_csv,
    resolve_create_campaigns,
    resolve_archive_campaign,
    resolve_update_campaign,
    resolve_skip_campaign_conversation,
    resolve_control_campaign,
    resolve_hold_campaign_conversation,
    resolve_record_campaign_conversation,
)
from krispcall.campaigns.entrypoints.graphql.resolvers.queries import (
    resolve_callScript_by_campaign_id,
    resolve_campaign_analytics,
    resolve_campaign_callScripts_list,
    resolve_campaign_callscript,
    resolve_campaign_contact_detail_lst,
    resolve_campaign_contact_list,
    resolve_campaign_count,
    resolve_campaign_details,
    resolve_campaign_voicemail,
    resolve_campaign_voicemail_list,
    resolve_campaign_list,
    resolve_campaign_callScripts_attribute_list,
    resolve_campaign_stats,
    resolve_campaign_note,
)

query = QueryType()
mutation = MutationType()

# bind query fields
query.set_field("getCampaignContactList", resolve_campaign_contact_list)
query.set_field(
    "getCampaignContactDetailList", resolve_campaign_contact_detail_lst
)
query.set_field("getCampaignVoiceMailList", resolve_campaign_voicemail_list)
query.set_field("getCallScriptById", resolve_callScript_by_campaign_id)
query.set_field("getCampaignCallScriptList", resolve_campaign_callScripts_list)
query.set_field(
    "getCampaignCallScriptAttributeList",
    resolve_campaign_callScripts_attribute_list,
)
query.set_field(
    "getCampaignsList",
    resolve_campaign_list,
)

query.set_field(
    "campaignAnalytics",
    resolve_campaign_analytics,
)

query.set_field(
    "campaignStats",
    resolve_campaign_stats,
)


query.set_field(
    "campaignNote",
    resolve_campaign_note,
)

query.set_field("campaignCallScript", resolve_campaign_callscript)
query.set_field("campaignVoicemail", resolve_campaign_voicemail)

query.set_field(
    "campaignDetails",
    resolve_campaign_details,
)

query.set_field("campaignsCount", resolve_campaign_count)


# bind mutation fields
mutation.set_field(
    "createCampaignContactList", resolve_create_contact_list_with_csv
)
mutation.set_field(
    "uploadCampaignContactDetailCSV", resolve_upload_contact_detail_csv
)
mutation.set_field(
    "updateCampaignContactList", resolve_update_campaign_contact_list
)
mutation.set_field(
    "addCampaignContactDetail", resolve_add_campaign_contact_detail
)

mutation.set_field(
    "deleteCampaignContactDetails", resolve_delete_campaign_contact_detail
)
mutation.set_field("addCampaignVoicemailDrop", resolve_add_campaign_voicemail)
mutation.set_field(
    "updateCampaignVoicemailDrop", resolve_update_campaign_voicemail
)
mutation.set_field("addCampaignCallScripts", resolve_add_campaign_callscripts)
mutation.set_field(
    "updateCampaignCallScripts", resolve_update_campaign_callscripts
)
mutation.set_field("createCampaigns", resolve_create_campaigns)
mutation.set_field("archiveCampaign", resolve_archive_campaign)
mutation.set_field("updateCampaign", resolve_update_campaign)
mutation.set_field("controlCampaign", resolve_control_campaign)
mutation.set_field("createCampaignCallNote", resolve_add_campaign_call_note)
mutation.set_field("updateCampaignCallNote", resolve_update_campaign_call_note)
mutation.set_field(
    "skipCampaignConversation", resolve_skip_campaign_conversation
)
mutation.set_field(
    "holdCampaignConversation", resolve_hold_campaign_conversation
)
mutation.set_field(
    "recordCampaignConversation", resolve_record_campaign_conversation
)

mutation.set_field(
    "campaignVoicemailDrop",
    resolve_campaign_voicemail_drop,
)
