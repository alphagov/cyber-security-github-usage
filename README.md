# cyber-security-github-usage
Lambda to report on github usage stats from pre-commit hook invocations

## usage 

When someone runs the install script for detect secrets:
1. They authenticate with Github
2. A message gets sent to the alert_processor endpoint
3. It records their username in SSM with a random generated token string
4. It passes the token back and saves it in the github global config.

The usage lambda runs daily on a cron:
1. Checks the membership of alphagov
2. Checks the list of users in SSM
3. Removes anyone from SSM who's no longer in alphagov
4. Reports the number of registered users of detect secrets as a percentage of the alphagov membership.

The random token was intended to be used on another pre-commit hook so we could record when a user commits with detect secrets enabled.
So for detect secrets we'd have 3 metrics:
1. % of alphagov members
2. % of (active) repos with a .secrets.baseline
3. % of commits protected by pre-commit

## audit

The aim if the audit is to capture the membership and access of 
github accounts to a github organisation. It looks at membership
of the organisation, membership of teams within the 
organisation and then at access to repositories within  
the organisation both as contributors and via 
membership of teams. 
 
The audit is run on a schedule. The audit can also be kicked off manually by an event 

```json
{"action":"audit"}
``` 

Which calls the audit.start function. 

From there the lambda is repeatedly 
triggered by SNS publish/subscribe 
until all the audit actions have 
completed. 

`audit.start`
- `log_org_membership`
- `log_org_teams`
    - `log_org_team_membership` for each team
    - `log_org_team_repos` for each team
        - `log_org_repo_team_members` for each team repo
- `log_org_repos`
    - `log_org_repo_contributors` for each repo