def ruby_sample() -> dict:
    return {
        "message": "Send account.linkedin_id as LI apply connect account identifier, skip if blank",
        "code": """
        diff --git a/app/models/concerns/candidates/apply_connect_signals_support.rb b/app/models/concerns/candidates/apply_connect_signals_support.rb
        index 636cae7e69d..6c0d4cece4e 100644
        --- a/app/models/concerns/candidates/apply_connect_signals_support.rb
        +++ b/app/models/concerns/candidates/apply_connect_signals_support.rb
        @@ -17,6 +17,8 @@ module Candidates
        
             def should_send_hearback_signal?(signal)
               return false unless linkedin_job_application_id.present?
        +      return false unless account.linkedin_id.present?
        +
               !linkedin_apply_connect_info&.already_sent?(signal)
             end
           end
        diff --git a/app/services/candidates/bulk/disqualifier.rb b/app/services/candidates/bulk/disqualifier.rb
        index 92fae6fe806..a96f765cb71 100644
        --- a/app/services/candidates/bulk/disqualifier.rb
        +++ b/app/services/candidates/bulk/disqualifier.rb
        @@ -14,7 +14,7 @@ module Candidates
               end
        
               def perform
        -        candidates_to_be_updated = Candidate.where(id: candidate_ids).order(:id).includes(:linkedin_apply_connect_info)
        +        candidates_to_be_updated = Candidate.where(id: candidate_ids).order(:id).includes(:account, :linkedin_apply_connect_info)
                 timestamp = Time.zone.now
                 candidates_to_be_updated.update_all({ disqualified: true,
                                                       disqualification_reason: disqualification_reason,
        diff --git a/app/services/linkedin/apply_connect_signal_updater.rb b/app/services/linkedin/apply_connect_signal_updater.rb
        index c85d1f87f52..8610f51ea9b 100644
        --- a/app/services/linkedin/apply_connect_signal_updater.rb
        +++ b/app/services/linkedin/apply_connect_signal_updater.rb
        @@ -59,7 +59,7 @@ module Linkedin
                 "jobApplicationId": candidate.linkedin_job_application_id,
                 "action": signal.upcase,
                 "performedAt": timestamp_in_epoch_with_milliseconds,
        -        "integrationContext": account.linkedin_organization&.rsc_organization_id
        +        "integrationContext": account.linkedin_id
               }
             end
        
        diff --git a/test/models/concerns/candidates/apply_connect_signals_support_test.rb b/test/models/concerns/candidates/apply_connect_signals_support_test.rb
        new file mode 100644
        index 00000000000..89c3f4c42a7
        --- /dev/null
        +++ b/test/models/concerns/candidates/apply_connect_signals_support_test.rb
        @@ -0,0 +1,35 @@
        +require "test_helper"
        +
        +module Candidates
        +  class ApplyConnectSignalsSupportTest < ActiveSupport::TestCase
        +
        +    test "should_send_hearback_signal?" do
        +      account = Account.new(linkedin_id: "foo_linkedin_id")
        +      candidate = Candidate.new(account: account, linkedin_job_application_id: "foo_linkedin_job_application_id")
        +
        +      assert candidate.should_send_hearback_signal?(Candidates::ApplyConnectSignalsSupport::APPLICATION_VIEWED_SIGNAL)
        +    end
        +
        +    test "should not send hearback signal if candidate does not have a linkedin_job_application_id" do
        +      account = Account.new(linkedin_id: "foo_linkedin_id")
        +      candidate = Candidate.new(account: account)
        +
        +      refute candidate.should_send_hearback_signal?(Candidates::ApplyConnectSignalsSupport::APPLICATION_VIEWED_SIGNAL)
        +    end
        +
        +    test "should not send hearback signal if account does not have a linkedin_id" do
        +      account = Account.new
        +      candidate = Candidate.new(account: account, linkedin_job_application_id: "foo_linkedin_job_application_id")
        +
        +      refute candidate.should_send_hearback_signal?(Candidates::ApplyConnectSignalsSupport::APPLICATION_VIEWED_SIGNAL)
        +    end
        +
        +    test "should not send hearback signal if already sent" do
        +      account = Account.new(linkedin_id: "foo_linkedin_id")
        +      candidate = Candidate.new(account: account, linkedin_job_application_id: "foo_linkedin_job_application_id")
        +      candidate.expects(:linkedin_apply_connect_info).returns(mock("linkedin_apply_connect_info", already_sent?: true))
        +
        +      refute candidate.should_send_hearback_signal?(Candidates::ApplyConnectSignalsSupport::APPLICATION_VIEWED_SIGNAL)
        +    end
        +  end
        +end
        diff --git a/test/services/linkedin/apply_connect_signal_updater_test.rb b/test/services/linkedin/apply_connect_signal_updater_test.rb
        index 9236f8de30a..a78a11a9f87 100644
        --- a/test/services/linkedin/apply_connect_signal_updater_test.rb
        +++ b/test/services/linkedin/apply_connect_signal_updater_test.rb
        @@ -11,12 +11,12 @@ module Linkedin
             attr_reader :candidate
        
             test "process" do
        -      rsc_id = "urn:li:organization:10414692"
        +      linkedin_id = "urn:li:organization:10414692"
               timestamp = get_timestamp
        +      @account.update_columns(linkedin_id: linkedin_id)
        
               # Send signal even if apply connect toggle disabled
               @account.linkedin_integration.update!(apply_connect: "disabled")
        -      LinkedinOrganization.any_instance.expects(rsc_organization_id: rsc_id)
        
               mock_retriever = mock("mock_retriever")
               Linkedin::AccessTokenRetriever.expects(:new).with(@account).returns(mock_retriever)
        @@ -25,7 +25,7 @@ module Linkedin
        
               refute @candidate.linkedin_apply_connect_info.already_sent?(Candidates::ApplyConnectSignalsSupport::APPLICATION_REJECTED_SIGNAL)
        
        -      stub_request_signal(rsc_id, "application_rejected", @candidate.linkedin_job_application_id, timestamp)
        +      stub_request_signal(linkedin_id, "application_rejected", @candidate.linkedin_job_application_id, timestamp)
               Linkedin::ApplyConnectSignalUpdater.process(@candidate.id, "application_rejected", timestamp)
               @candidate.reload
               assert @candidate.linkedin_apply_connect_info.already_sent?(Candidates::ApplyConnectSignalsSupport::APPLICATION_REJECTED_SIGNAL)
        @@ -46,14 +46,14 @@ module Linkedin
               (Time.now.to_f * 1000).to_i
             end
        
        -    def stub_request_signal(rsc_id, event_type, linkedin_job_application_id, timestamp)
        +    def stub_request_signal(account_linkedin_id, event_type, linkedin_job_application_id, timestamp)
               stub_request(:post, "https://api.linkedin.com/v2/jobApplicationLifecycleActions")
                 .with(
                   body: {
                     "jobApplicationId": linkedin_job_application_id,
                     "action": event_type.upcase,
                     "performedAt": timestamp,
        -            "integrationContext": rsc_id
        +            "integrationContext": account_linkedin_id
                   }.to_json,
                   headers: {
                     "Accept": "*/*",
     """,
    }
