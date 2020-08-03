# cyber-security-github-usage
Lambda to report on github usage stats from pre-commit hook invocations

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