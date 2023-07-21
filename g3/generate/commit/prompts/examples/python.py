# flake8: noqa
def python_sample() -> dict:
    return {
        "message": "Refactor Updaters to always return dict for changes",
        "code": """
                diff --git a/antifraud/services/account_activities/updater.py b/antifraud/services/account_activities/updater.py
        index 1643678..e48b89e 100644
        --- a/antifraud/services/account_activities/updater.py
        +++ b/antifraud/services/account_activities/updater.py
        @@ -1,4 +1,4 @@
        -from typing import Any, Dict, Optional, Tuple
        +from typing import Any, Dict, Tuple
        
         from ml_utils.helpers.date import to_datetime
        
        @@ -13,7 +13,7 @@ class Updater:
             def __init__(self):
                 self.state_manager = StateManager()
        
        -    def update(self, value: dict[str, Any], trigger: str) -> Tuple[Account, Optional[Dict[str, Any]]]:
        +    def update(self, value: dict[str, Any], trigger: str) -> Tuple[Account, Dict[str, Any]]:
                 account = Account.get_or_create(uid=value.get("uid"))  # type: ignore
                 account.id = value.get("id")
                 changed, changes = Comparator.differ_significantly(account, Account.of(value))
        @@ -22,7 +22,7 @@ class Updater:
                         f"Ignoring Labb account activity of account '{value.get('uid')}' with trigger '{trigger}' "
                         f"(approval status did not change)"
                     )
        -            return account, None
        +            return account, {}
        
                 account.state = self.state_manager.calculate_account_state(account, changes)
                 account.approval_status = ApprovalStatus(value.get("approval_status"))
        diff --git a/antifraud/services/accounts/updater.py b/antifraud/services/accounts/updater.py
        index 7bdee32..e2592a8 100644
        --- a/antifraud/services/accounts/updater.py
        +++ b/antifraud/services/accounts/updater.py
        @@ -13,7 +13,7 @@ class Updater:
                 self.state_manager = StateManager()
        
             @stats.time(name="timers", tags=["metric_instance:accounts", "function:update"])
        -    def update(self, account_dict: dict[str, Any], trigger: str) -> Tuple[Account, Optional[Dict[str, Any]]]:
        +    def update(self, account_dict: dict[str, Any], trigger: str) -> Tuple[Account, Dict[str, Any]]:
                 "
                 Updates the account, if needed, based on the account message received
                 :param account_dict: The new in-memory Account from Kafka
        @@ -26,7 +26,7 @@ class Updater:
                     logger.info(
                         f"Ignoring account '{account_dict.get('uid')}' with trigger '{trigger}' (not significant changes)"
                     )
        -            return account, None
        +            return account, {}
        
                 logger.info(
                     f"{'Creating' if trigger.endswith('created') or account.id is None else 'Updating'} "
        diff --git a/antifraud/services/company_social_profiles/updater.py b/antifraud/services/company_social_profiles/updater.py
        index e5e205a..df509a7 100644
        --- a/antifraud/services/company_social_profiles/updater.py
        +++ b/antifraud/services/company_social_profiles/updater.py
        @@ -1,4 +1,4 @@
        -from typing import Any, Dict, List, Optional, Tuple
        +from typing import Any, Dict, List, Tuple
        
         from antifraud import logger, stats
         from antifraud.db.antifraud.models import Account, CompanySocialProfile
        @@ -10,7 +10,7 @@ class Updater:
                 self.accounts_state_manager = AccountsStateManager()
        
             @stats.time(name="timers", tags=["metric_instance:company_social_profiles", "function:update"])
        -    def update(self, company_social_profile_msg: dict) -> List[Tuple[Account, Optional[Dict[str, Any]]]]:
        +    def update(self, company_social_profile_msg: dict) -> List[Tuple[Account, Dict[str, Any]]]:
                 company_social_profile = CompanySocialProfile.get(company_social_profile_msg["id"])
                 company_social_profile = CompanySocialProfile.of(company_social_profile_msg, company_social_profile)
        
        @@ -18,7 +18,7 @@ class Updater:
                 results = []
                 for account_w_ids in accounts_w_ids:
                     account = Account.get_or_create(uid=account_w_ids["uid"], for_update=True, join_tables=True)
        -            changes = None
        +            changes = {}
                     if (
                         account.company_social_profile_id is None
                         or account.company_social_profile_id != company_social_profile.id
        @@ -27,11 +27,9 @@ class Updater:
                         account.website_url = company_social_profile_msg.get("domain")  # the domain before using the validator
                         account.domain = company_social_profile.domain
                         account.company_social_profile = company_social_profile
        -                changes = {
        -                    "company_social_profile_id": {
        -                        "from": account.company_social_profile_id,
        -                        "to": company_social_profile.id,
        -                    }
        +                changes["company_social_profile_id"] = {
        +                    "from": account.company_social_profile_id,
        +                    "to": company_social_profile.id,
                         }
                     account.state = self.accounts_state_manager.calculate_account_state(account, changes)
        
        diff --git a/antifraud/services/jobs/updater.py b/antifraud/services/jobs/updater.py
        index c1a960c..3e8c794 100644
        --- a/antifraud/services/jobs/updater.py
        +++ b/antifraud/services/jobs/updater.py
        @@ -1,4 +1,4 @@
        -from typing import Any, Dict, Optional, Tuple, cast
        +from typing import Any, Dict, Tuple, cast
        
         from antifraud import logger, stats
         from antifraud.db.antifraud.models import Account, Job
        @@ -11,13 +11,13 @@ class Updater:
                 self.state_manager = StateManager()
        
             @stats.time(name="timers", tags=["metric_instance:jobs", "function:update"])
        -    def update(self, job_dict: dict[str, Any], trigger: str) -> Tuple[Account, Optional[Dict[str, Any]]]:
        +    def update(self, job_dict: dict[str, Any], trigger: str) -> Tuple[Account, Dict[str, Any]]:
                 account = Account.get_or_create(uid=cast(str, job_dict.get("account_uid")), join_tables=True, for_update=True)
                 job = account.get_job(job_dict["id"])
                 changed, changes = Comparator.differ_significantly(job, Job.of(job_dict))
                 if not changed:
                     logger.info(f"Ignoring job '{job_dict.get('id')}' with trigger '{trigger}' (not significant changes)")
        -            return account, None
        +            return account, {}
                 logger.info(
                     f"{'Creating' if trigger.endswith('created') else 'Updating'} "
                     f"job '{job_dict.get('id')}' with changes {changes}"
        diff --git a/antifraud/services/members/updater.py b/antifraud/services/members/updater.py
        index 99ed86d..9556540 100644
        --- a/antifraud/services/members/updater.py
        +++ b/antifraud/services/members/updater.py
        @@ -1,4 +1,4 @@
        -from typing import Any, Dict, Optional, Tuple, cast
        +from typing import Any, Dict, Tuple, cast
        
         from antifraud import logger, stats
         from antifraud.db.antifraud.models import Account, Member
        @@ -11,13 +11,13 @@ class Updater:
                 self.accounts_state_manager = AccountsStateManager()
        
             @stats.time(name="timers", tags=["metric_instance:members", "function:update"])
        -    def update(self, member_msg: dict, trigger: str) -> Tuple[Account, Optional[Dict[str, Any]]]:
        +    def update(self, member_msg: dict, trigger: str) -> Tuple[Account, Dict[str, Any]]:
                 account = Account.get_or_create(uid=cast(str, member_msg.get("account_uid")), join_tables=True, for_update=True)
                 member = account.get_member(member_msg.get("id"))
                 changed, changes = Comparator.differ_significantly(member, Member.of(member_msg))
                 if not changed:
                     logger.info(f"Ignoring member '{member_msg.get('id')}' with trigger '{trigger}' (not significant changes)")
        -            return account, None
        +            return account, {}
                 logger.info(
                     f"{'Creating' if trigger.endswith('created') else 'Updating'} "
                     f"member '{member_msg.get('id')}' with changes {changes}"
    """,
    }
