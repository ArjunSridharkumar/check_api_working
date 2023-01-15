# -*- coding: utf-8 -*-
import json
import pandas as pd
import stscraper as scraper
from datetime import datetime as dt
import time
import re
from urllib.error import HTTPError
import requests

def issue_pr_timeline(self, repo, issue_id):
    """ Return timeline on an issue or a pull request
    :param repo: str 'owner/repo'url
    :param issue_id: int, either an issue or a Pull Request id
    """
    url = "repos/%s/issues/%s/timeline" % (repo, issue_id)
    events = self.request(url, paginate=True, state='all')
    for event in events:
        # print('repo: ' + repo + ' issue: ' + str(issue_id) + ' event: ' + event['event'])
        if event['event'] == 'cross-referenced':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': "",
                'created_at': event.get('created_at'),
                'id': event['source']['issue']['number'],
                'repo': event['source']['issue']['repository']['full_name'],
                'type': 'pull_request' if 'pull_request' in event['source']['issue'].keys() else 'issue',
                'state': event['source']['issue']['state'],
                'assignees': event['source']['issue']['assignees'],
                'label': "",
                'body': ''
            }
        elif event['event'] == 'referenced':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': event['commit_id'],
                'created_at': event['created_at'],
                'id': '',
                'repo': '',
                'type': 'commit',
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
        elif event['event'] == 'labeled':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': '',
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "label",
                'state': '',
                'assignees': '',
                'label': event['label']['name'],
                'body': ''
            }
        elif event['event'] == 'committed':
            yield {
                'event': event['event'],
                'author': event['author']['name'],
                'email': event['author']['email'],
                'author_type': '',
                'author_association': '',
                'commit_id': event['sha'],
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "commit",
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
        elif event['event'] == 'reviewed':
            author = event['user'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': event['author_association'],
                'commit_id': '',
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "review",
                'state': event['state'],
                'assignees': '',
                'label': '',
                'body': ''
            }
        elif event['event'] == 'commented':
            yield {
                'event': event['event'],
                'author': event['user']['login'],
                'email': '',
                'author_type': event['user']['type'],
                'author_association': event['author_association'],
                'commit_id': '',
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "comment",
                'state': '',
                'assignees': '',
                'label': '',
                'body': event['body']
            }
        elif event['event'] == 'assigned':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': '',
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "comment",
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
        elif event['event'] == 'closed':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': event['commit_id'],
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "close",
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
        elif event['event'] == 'subscribed':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': event['commit_id'],
                'created_at': event.get('created_at'),
                'id': event['commit_id'],
                'repo': '',
                'type': "subscribed",
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
        elif event['event'] == 'merged':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': event['commit_id'],
                'created_at': event.get('created_at'),
                'id': event['commit_id'],
                'repo': '',
                'type': "merged",
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
        elif event['event'] == 'mentioned':
            author = event['actor'] or {}
            yield {
                'event': event['event'],
                'author': author.get('login'),
                'email': '',
                'author_type': author.get('type'),
                'author_association': '',
                'commit_id': '',
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "mentioned",
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
        else:
            yield {
                'event': event['event'],
                'author': '',
                'email': '',
                'author_type': '',
                'author_association': '',
                'commit_id': '',
                'created_at': event.get('created_at'),
                'id': '',
                'repo': '',
                'type': "",
                'state': '',
                'assignees': '',
                'label': '',
                'body': ''
            }
def github_type_of_link_identifier(link):
    #import pdb;pdb.set_trace()
    try:
        temp_user_name = re.split("github.com/|github.io", link)[1]
    except Exception as e:
        import pdb;pdb.set_trace()
    user_name = temp_user_name.split("/")[0]
    repo_name = temp_user_name.split("/")[1]
    #repo_name = link.split("github.com/")[2]
    repo_slug = user_name + "/" + repo_name

    #Check for commit first
    if "commit" in link:
        commit_string = re.search(r"commit\/\w+", link)
        if commit_string:
            type_of_link = "commit"
            event_id = commit_string.group(0)
            event_id = event_id.split("/")[1]
            return repo_slug, type_of_link,event_id
        else:
            pass

    #Check for pull request
    if "pull" in link:
        pull_request_string  = re.search(r'pull\/\w+', link)
        if pull_request_string:
            type_of_link = "pull request"
            event_id = pull_request_string.group(0)
            event_id= event_id.split("/")[1]
            return repo_slug, type_of_link, event_id
        else:
            pass

    #Check for isssue
    if "issues" in link:
        issues_string  = re.search(r'issues\/\d+', link)
        if issues_string:
            type_of_link = "issue"
            event_id = issues_string.group(0)
            event_id = event_id.split("/")[1]
            return repo_slug, type_of_link, event_id
        else:
            pass

    type_of_link = 'NA'
    event_id = None
    return repo_slug,type_of_link, event_id

# def add_user_to_dict(json_data,user_dict,user_miss_dict):


# def repo_get_commit_arjun(self, repo_slug, commit_hash):
#     import pdb;pdb.set_trace()
#     """Get details for a single commit."""
#     url = "repos/%s/commits/%s" % (repo_slug, commit_hash)
#     events = self.request(url, paginate=True, state='all').json()
#     # for event in events:
#     #     yield{
#     #         'author_login':event['author']['login'],
#     #         'committer_login':event['committer']['login']
#     #     }
#     # https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#get-a-commit
#     return events

def github_issue_pull_fetch_data(CVE_ID,gh_api,api,headers,repo_slug,link,timeline_data,nvd_date_formatted,event_id,token,user_dict):
    # Pull request data gathering.
    #print("PR link found")
    pull_id = event_id
    try:
        int_pull_id = int(pull_id)
    except Exception as e:
        print ("Pull id not caught")
        #raise(e)
    generator_value  = False
    print("PR function in")
    try:
        timeline = issue_pr_timeline(gh_api,repo_slug,int(pull_id))
    except Exception as e:
        generator_value  = True
        print ("Issue pr timeline failed")
        main_pull_miss_dict = {'CVE_ID':[],'link':[]}
        main_pull_miss_dict['CVE_ID'].append(CVE_ID)
        main_pull_miss_dict['link'].append(link)
        main_pull_miss_dict['type'].append("Main Pull")
        main_pull_miss_dict_df = pd.DataFrame(main_pull_miss_dict)
        main_pull_miss_df = pd.read_csv("pull_miss_dict_df.csv")
        main_pull_miss_df = main_pull_miss_df.append(main_pull_miss_dict_df, ignore_index=True)
        main_pull_miss_df.to_csv("pull_miss_dict_df.csv", index=False)

        # output_data = pd.read_csv("output_data.csv")
        # output_data = output_data.append(timeline_data)
        # output_data.to_csv("output_data.csv", index=False)
        return [timeline_data,user_dict]
        #raise(e)
    print("PR function out")
    # print (timeline)

    
    
    # _exhausted = object()
    
    # if next(timeline, _exhausted) is _exhausted:
    #     print('generator is empty')
    #     generator_value = True
    #     generator_empty_dict = {'CVE_ID':[],'link':[]}    
    #     generator_empty_dict['CVE_ID'].append(CVE_ID)
    #     generator_empty_dict['link'].append(link)
    #     generator_df = pd.read_csv("generator_empty.csv")
    #     generator_empty_dict_df = pd.DataFrame(generator_empty_dict)
    #     generator_df.append(generator_empty_dict_df, ignore_index=True)
    #     generator_df.to_csv("generator_empty.csv", index=False)
        
    
     #Adding the first comment of the pull request and issue
    try:
        print ("pr creation_date", repo_slug)
        print ("pr creation_date", pull_id)
        url = "repos/%s/issues/%s" % (repo_slug, pull_id)
        url = "https://api.github.com/"  + url
        #first_set_events = gh_api.request(url, paginate=True, state='all')
        headers = {'Authorization': 'token' + token}
        print("PR first comment in")
        try:
            json_value_org = requests.get(url, headers=headers).json()
        except Exception as e:
            pull_miss_dict = {'CVE_ID':[], 'link':[], "type":[]}
            pull_miss_dict['CVE_ID'].append(CVE_ID)
            pull_miss_dict['link'].append(link)
            pull_miss_dict['type'].append("Pull request first comment")
            pull_miss_dict_df = pd.DataFrame(pull_miss_dict)
            pull_miss_df = pd.read_csv("pull_miss_dict_df.csv")
            pull_miss_df = pull_miss_df.append(pull_miss_dict_df, ignore_index=True)
            pull_miss_df.to_csv("pull_miss_dict_df.csv", index=False)
        if "created_at" in list(json_value_org.keys()):
            first_set_events = json_value_org['created_at']
            event_created_at_formatted = dt.strptime(first_set_events, "%Y-%m-%dT%H:%M:%SZ")
            if nvd_date_formatted > event_created_at_formatted:
                timeline_data['CVE_ID'].append(CVE_ID)
                timeline_data['Timestamp'].append(first_set_events)
                event_name = "Creation time event"
                timeline_data['Event'].append(event_name)
                timeline_data['Event_ID'].append(pull_id)
                #user_dict = {'CVE_ID':[], 'login_name':[], 'author_association':[],'author_type':[], 'link':[]}
                #user_miss_dict = {'CVE_ID':[],'link':[]}
                user_login_name = json_value_org['user']['login']
                user_author_association = json_value_org['author_association']
                user_author_type = json_value_org['user']['type']
                user_dict['CVE_ID'].append(CVE_ID)
                user_dict['login_name'].append(user_login_name)
                user_dict['author_association'].append(user_author_association)
                user_dict['author_type'].append(user_author_type)
                user_dict['link'].append(link)
        else:
            if "message" in json_value_org.keys():
                message_value = json_value_org['message']
                if "rate limit" in message_value:
                    pull_miss_dict = {'CVE_ID':[], 'link':[], "type":[]}
                    pull_miss_dict['CVE_ID'].append(CVE_ID)
                    pull_miss_dict['link'].append(link)
                    pull_miss_dict['type'].append("Pull request first comment")
                    pull_miss_dict_df = pd.DataFrame(pull_miss_dict)
                    pull_miss_df = pd.read_csv("pull_miss_dict_df.csv")
                    pull_miss_df = pull_miss_df.append(pull_miss_dict_df, ignore_index=True)
                    pull_miss_df.to_csv("pull_miss_dict_df.csv", index=False)
                    #added_pull = True
                    #return [timeline_data, added_pull, omitted_dict, other_links_dict, main_pull_miss_dict]
    except Exception as e:
        pull_miss_dict = {'CVE_ID':[], 'link':[], "type":[]}
        pull_miss_dict['CVE_ID'].append(CVE_ID)
        pull_miss_dict['link'].append(link)
        pull_miss_dict['type'].append("Pull request first comment")
        pull_miss_dict_df = pd.DataFrame(pull_miss_dict)
        pull_miss_df = pd.read_csv("pull_miss_dict_df.csv")
        pull_miss_df = pull_miss_df.append(pull_miss_dict_df, ignore_index=True)
        pull_miss_df.to_csv("pull_miss_dict_df.csv", index=False)
    print("PR first comment out")

    #Add the data to timeline data
    try:    
        if not generator_value:
            for pr in timeline:
                print ("Inside PR loop started")
                #import  pdb;pdb.set_trace()
                #print("PR new data")
                pr_creation_date = pr['created_at']
                pr_creation_date_formatted = None
                #print("B4 IF ELSE")

                if ((pr['commit_id'] is None) or (pr['commit_id'] == '')) and ((pr['created_at'] is None) or (pr['created_at'] == "")):
                    continue
                # if (pr_creation_date == '') or (pr_creation_date is None):
                #     #print("in IF")
                #     continue
                else:
                    #print("IN ELSE")
                    #Call the commit info related function to get details
                    print ("commit parsing inside pr started")
                    commit_bool = True
                    if (pr_creation_date is None) and (pr['event'] == 'committed') and ((pr['commit_id'] is not None) and (pr['commit_id'] != '')):
                        try:
                            #print("IN COMMIT")
                            commit_hash = pr['commit_id']
                            commit_details  = gh_api.repo_commit(repo_slug,commit_hash)
                        except HTTPError as e:
                            print ("rate limit exceeded inside the PR commit fetch") 
                            if (e.response.status_code == 401):
                                time.sleep(2)
                                try:
                                    commit_details  = gh_api.repo_commit(repo_slug,commit_hash)
                                except Exception as e:
                                    commits_miss_dict = {'CVE_ID':[], 'repo_slug':[],"commit_hash":[], "link":[], "role":[]}
                                    commits_miss_dict['CVE_ID'].append(CVE_ID)
                                    commits_miss_dict['repo_slug'].append(repo_slug)
                                    commits_miss_dict['commit_hash'].append(commit_hash)
                                    commits_miss_dict['link'].append(link)
                                    commits_miss_dict['role'].append("PR commit")
                                    commits_miss_dict_df = pd.DataFrame(commits_miss_dict)
                                    commits_miss_df = pd.read_csv("commits_miss_dict_df.csv")
                                    commits_miss_df = commits_miss_df.append(commits_miss_dict_df, ignore_index=True)
                                    commits_miss_df.to_csv("commits_miss_dict_df.csv", index=False)
                                    commit_bool = False

                            print("Inside PR Commit fetch not working ")
                            #print(e)
                            commits_miss_dict = {'CVE_ID':[], 'repo_slug':[],"commit_hash":[], "link":[], "role":[]}
                            commits_miss_dict['CVE_ID'].append(CVE_ID)
                            commits_miss_dict['repo_slug'].append(repo_slug)
                            commits_miss_dict['commit_hash'].append(commit_hash)
                            commits_miss_dict['link'].append(link)
                            commits_miss_dict['role'].append("PR commit")
                            commits_miss_dict_df = pd.DataFrame(commits_miss_dict)
                            commits_miss_df = pd.read_csv("commits_miss_dict_df.csv")
                            commits_miss_df = commits_miss_df.append(commits_miss_dict_df, ignore_index=True)
                            commits_miss_df.to_csv("commits_miss_dict_df.csv", index=False)
                            commit_bool = False
                            
                            #continue
                        print ("commit parsing inside pr ended")
                        try:
                            commit_author_date = commit_details['commit']['author']['date']
                            commit_date = commit_details['commit']['committer']['date']
                        except Exception as e:
                            commit_date = None
                            import pdb;pdb.set_trace()

                        if (commit_date is not None):
                            commit_date_formatted = dt.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
                            commit_author_date_formatted = dt.strptime(commit_author_date, "%Y-%m-%dT%H:%M:%SZ")
                        
                        final_commit_date = commit_date_formatted

                        pr_creation_date = final_commit_date

                        print ("Pr commit is parsed")
                        try:
                            if type(pr_creation_date) is str:
                                pr_creation_date_formatted = dt.strptime(pr_creation_date, "%Y-%m-%dT%H:%M:%SZ")
                            else:
                                pr_creation_date_formatted = pr_creation_date
                        except Exception as e:
                            print ("Date type mismatch")
                            import pdb;pdb.set_trace()

                        if nvd_date_formatted > pr_creation_date_formatted:
                            try:
                                commit_author_name = commit_details['author']['login']
                                commit_author_type = commit_details['author']['type']
                                commit_author_association = "Author"
                                if len(commit_author_name) > 0:
                                    user_dict['CVE_ID'].append(CVE_ID)
                                    user_dict['link'].append(link)
                                    user_dict['login_name'].append(commit_author_name)
                                    user_dict['author_association'].append(commit_author_association)
                                    user_dict['author_type'].append(commit_author_type)
                            except Exception as e:
                                user_miss_dict = {'CVE_ID':[],'link':[], "role":[], "commit_repo_slug": [],"commit_hash":[]}
                                user_miss_dict['CVE_ID'].append(CVE_ID)
                                user_miss_dict['link'].append(link)
                                user_miss_dict['role'].append("author")
                                user_miss_dict['commit_repo_slug'].append(repo_slug)
                                user_miss_dict['commit_hash'].append(commit_hash)
                                user_miss_dict_df = pd.DataFrame(user_miss_dict)
                                user_miss_df = pd.read_csv("user_miss_dict_df.csv")
                                user_miss_df = user_miss_df.append(user_miss_dict_df, ignore_index=True)
                                user_miss_df.to_csv("user_miss_dict_df.csv", index=False)
                            try:
                                commit_commiter_name = commit_details['committer']['login']
                                commit_commiter_association = "Committer"
                                commit_commiter_type = commit_details['committer']['type']
                                if len(commit_commiter_name) > 0:
                                    user_dict['CVE_ID'].append(CVE_ID)
                                    user_dict['link'].append(link)
                                    user_dict['login_name'].append(commit_commiter_name)
                                    user_dict['author_association'].append(commit_commiter_association)
                                    user_dict['author_type'].append(commit_commiter_type)
                                    
                            except Exception as e:
                                user_miss_dict = {'CVE_ID':[],'link':[], "role":[], "commit_repo_slug": [],"commit_hash":[]}
                                user_miss_dict['CVE_ID'].append(CVE_ID)
                                user_miss_dict['link'].append(link)
                                user_miss_dict['role'].append("committer")
                                user_miss_dict['commit_repo_slug'].append(repo_slug)
                                user_miss_dict['commit_hash'].append(commit_hash)
                                user_miss_dict_df = pd.DataFrame(user_miss_dict)
                                user_miss_df = pd.read_csv("user_miss_dict_df.csv")
                                user_miss_df = user_miss_df.append(user_miss_dict_df, ignore_index=True)
                                user_miss_df.to_csv("user_miss_dict_df.csv", index=False)

            
                    #Conversion of pr_creation_date
                    #print ("Date conversion and matching")
                    try:
                        if type(pr_creation_date) is str:
                            pr_creation_date_formatted = dt.strptime(pr_creation_date, "%Y-%m-%dT%H:%M:%SZ")
                        else:
                            pr_creation_date_formatted = pr_creation_date
                    except Exception as e:
                        print ("Date type mismatch")
                        import pdb;pdb.set_trace()

                    if nvd_date_formatted > pr_creation_date_formatted:
                        #Check if date is earlier than NVD/public disclousure date
                        try:
                            timeline_data['CVE_ID'].append(CVE_ID)
                        except Exception as e:
                            import pdb;pdb.set_trace()
                        timeline_data['Timestamp'].append(pr_creation_date)
                        timeline_data['Event'].append(pr['event'])
                        
                        if pr['event'] != 'committed':
                            #user_dict = {'CVE_ID':[], 'login_name':[], 'author_association':[],'author_type':[], 'link':[]}
                            #user_miss_dict = {'CVE_ID':[],'link':[]}
                            user_login_name = pr['author']
                            user_author_association = pr['author_association']
                            user_author_type = pr['author_type']
                            user_dict['CVE_ID'].append(CVE_ID)
                            user_dict['link'].append(link)
                            user_dict['login_name'].append(user_login_name)
                            user_dict['author_association'].append(user_author_association)
                            user_dict['author_type'].append(user_author_type)    

                        #Assign event_id as commit id only for certain types of PRs
                        if (pr['event'] == "committed") or (pr['event'] == "merged") or (pr['event'] == "closed"):
                            #print ("event id calculatin")
                            #print (pr['event'])
                            timeline_data['Event_ID'].append(pr['commit_id'])
                        else:
                            timeline_data['Event_ID'].append(None)
            print("end of pr loop")
        else:
            print ("####### No looop iteration #######")
    except Exception as e:
        pull_miss_dict = {'CVE_ID':[], 'link':[], "type":[]}
        pull_miss_dict['CVE_ID'].append(CVE_ID)
        pull_miss_dict['link'].append(link)
        pull_miss_dict['type'].append("Pull request generator failed")
        pull_miss_dict_df = pd.DataFrame(pull_miss_dict)
        pull_miss_df = pd.read_csv("pull_miss_dict_df.csv")
        pull_miss_df = pull_miss_df.append(pull_miss_dict_df, ignore_index=True)
        pull_miss_df.to_csv("pull_miss_dict_df.csv", index=False)
    print("PR first comment out")


    # output_data = pd.read_csv("output_data.csv")
    # output_data = output_data.append(timeline_data)
    # output_data.to_csv("output_data.csv", index=False)
    return [timeline_data,user_dict]

def github_commit_fetch_data(CVE_ID,gh_api,repo_slug, link, timeline_data,nvd_date_formatted,event_id,user_dict):

    print ("Commit link found")
    commit_hash = event_id
    print ("repo_slug",repo_slug)
    print ("commit_hash",commit_hash)
 

    # if len(commit_hash) is not 40:
    #     diff_commits.append(commit_hash)
    #     diff_repos_commits.append(repo_slug)
    #     return timeline_data,added_commit,user_dict,user_miss_dict

    try:
        commits_timeline = gh_api.repo_commit(repo_slug,commit_hash)
    except Exception as e:
        #import pdb;pdb.set_trace()
        if (e.response.status_code == 401):
            print ("API rate limit exceeded")
            print ("Sleeping for 5 seconds")
            time.sleep(2)
            try:
                commits_timeline = gh_api.repo_commit(repo_slug,commit_hash)
            except Exception as e:
                commits_miss_dict = {'CVE_ID':[], 'repo_slug':[],"commit_hash":[], "link":[], "role":[]}
                commits_miss_dict['CVE_ID'].append(CVE_ID)
                commits_miss_dict['repo_slug'].append(repo_slug)
                commits_miss_dict['commit_hash'].append(commit_hash)
                commits_miss_dict['link'].append(link)
                commits_miss_dict['role'].append("Commit function")
                commits_miss_dict_df = pd.DataFrame(commits_miss_dict)
                commits_miss_df = pd.read_csv("commits_miss_dict_df.csv")
                commits_miss_df = commits_miss_df.append(commits_miss_dict_df, ignore_index=True)
                commits_miss_df.to_csv("commits_miss_dict_df.csv", index=False)

                # output_data = pd.read_csv("output_data.csv")
                # timeline_df = pd.DataFrame(timeline_data)
                # output_data = output_data.append(timeline_df, ignore_index=True)
                # output_data.to_csv("output_data.csv", index=False)

                user_dict_df = pd.DataFrame(user_dict)

                return timeline_data,user_dict

        print ("Commit data not found for Commit id: ", commit_hash)
        print("Repo slug is: ", repo_slug)
        commits_miss_dict = {'CVE_ID':[], 'repo_slug':[],"commit_hash":[], "link":[], "role":[]}
        commits_miss_dict['CVE_ID'].append(CVE_ID)
        commits_miss_dict['link'].append(link)
        commits_miss_dict['repo_slug'].append(repo_slug)
        commits_miss_dict['commit_hash'].append(commit_hash)
        commits_miss_dict['role'].append("Commit function")              
        commits_miss_dict_df = pd.DataFrame(commits_miss_dict)
        commits_miss_df = pd.read_csv("commits_miss_dict_df.csv")
        commits_miss_df = commits_miss_df.append(commits_miss_dict_df, ignore_index=True)
        commits_miss_df.to_csv("commits_miss_dict_df.csv", index=False)
        return timeline_data,user_dict
       
    try:
        commit_author_date = commits_timeline['commit']['author']['date']
        commit_date = commits_timeline['commit']['committer']['date']
    except Exception as e:
        commit_author_date = None
        commit_date = None
    #import pdb;pdb.set_trace()
    #commit_commiter_name = commits_timeline['committer']['login']
    commit_author_date_formatted = dt.strptime(commit_author_date,"%Y-%m-%dT%H:%M:%SZ")
    
    if (commit_date is not None):
        commit_date_formatted = dt.strptime(commit_date,"%Y-%m-%dT%H:%M:%SZ")
        final_commit_date = commit_date_formatted
    print ("end of commit")
    if nvd_date_formatted > final_commit_date:
        # Check if date is earlier than NVD/public disclousure date
        timeline_data['CVE_ID'].append(CVE_ID)
        timeline_data['Timestamp'].append(final_commit_date)
        timeline_data['Event'].append("Commit")

        # Assign event_id as commit hash only for certain types of PRs
        timeline_data['Event_ID'].append(commit_hash)
        try:
            commit_author_name = commits_timeline['author']['login']
            commit_author_association = "Author"
            commit_author_type = commits_timeline['author']['type']

            if len(commit_author_name) > 0:
                user_dict['CVE_ID'].append(CVE_ID)
                user_dict['link'].append(link)
                user_dict['login_name'].append(commit_author_name)
                user_dict['author_association'].append(commit_author_association)
                user_dict['author_type'].append(commit_author_type)
            
        except Exception as e:
            user_miss_dict = {'CVE_ID':[],'link':[], "role":[], "commit_repo_slug": [],"commit_hash":[]}
            user_miss_dict['CVE_ID'].append(CVE_ID)
            user_miss_dict['link'].append(link)
            user_miss_dict['role'].append("author")
            user_miss_dict['commit_repo_slug'].append(repo_slug)
            user_miss_dict['commit_hash'].append(commit_hash)
            user_miss_dict_df = pd.DataFrame(user_miss_dict)
            user_miss_df = pd.read_csv("user_miss_dict_df.csv")
            user_miss_df = user_miss_df.append(user_miss_dict_df, ignore_index=True)
            user_miss_df.to_csv("user_miss_dict_df.csv", index=False)
           

        try:
            commit_commiter_name = commits_timeline['committer']['login']
            commit_commiter_association = "Committer"
            commit_commiter_type = commits_timeline['committer']['type']

            if len(commit_commiter_name) > 0:
                user_dict['CVE_ID'].append(CVE_ID)
                user_dict['link'].append(link)
                user_dict['login_name'].append(commit_commiter_name)
                user_dict['author_association'].append(commit_commiter_association)
                user_dict['author_type'].append(commit_commiter_type)
        except Exception as e:
            user_miss_dict = {'CVE_ID':[],'link':[], "role":[], "commit_repo_slug": [],"commit_hash":[]}
            user_miss_dict['CVE_ID'].append(CVE_ID)
            user_miss_dict['link'].append(link)
            user_miss_dict['role'].append("committer")
            user_miss_dict['commit_repo_slug'].append(repo_slug)
            user_miss_dict['commit_hash'].append(commit_hash)
            user_miss_dict_df = pd.DataFrame(user_miss_dict)
            user_miss_df = pd.read_csv("user_miss_dict_df.csv")
            user_miss_df = user_miss_df.append(user_miss_dict_df, ignore_index=True)
            user_miss_df.to_csv("user_miss_dict_df.csv", index=False)            

       
    return timeline_data,user_dict

def github_parser_main(CVE_ID,link, nvd_date, timeline_data, user_dict):
    print ("======================")
    type_of_link = 'NA'
    try:
        nvd_date_formatted = dt.strptime(nvd_date, "%Y-%m-%dT%H:%MZ")
    except Exception as e:
        print ("NVD date conversion not working")
        #import pdb;pdb.set_trace()
        print(e)

    try:
        repo_slug, type_of_link, event_id = github_type_of_link_identifier(link)
    except Exception as e:
        print ("Type of link identifier is not working")
        print(e)
        type_of_link = 'NA'
        #types_of_link_dict['CVE_ID'].append(CVE_ID)
        #types_of_link_dict['link'].append(link)
        return timeline_data,user_dict
         
    list_of_lists=[]
    with open('tokens.txt') as f:
        for line in f:
            inner_list = [elt.strip()for elt in line.split('\n')]
            # in alternative, if you need to use the file content as numbers
            # inner_list = [int(elt.strip()) for elt in line.split(',')]
            list_of_lists = list_of_lists + inner_list
    list_of_lists = list(filter(lambda a: a != '', list_of_lists))
    # print (list_of_lists)
    #gh_api = ["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","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","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"]
    
    # try:
    #     gh_api =repoMethod(list_of_lists)
    # except Exception as e:
    #     raise(e)
    string_tokens = ",".join(list_of_lists)
    #token = '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' 
    token = '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'
    gh_api = scraper.GitHubAPI(string_tokens)
    # other_links_dict = {"CVE_ID":[], "link":[]}
    # type_of_link_df_output = pd.read_csv("type_of_link_df_output.csv")
    # type_of_link_df_output.append(pd.DataFrame({"CVE_ID":[CVE_ID],"type":[type_of_link]}))
    # type_of_link_df_output.to_csv("type_of_link_df_output.csv",index=False)
    #print (gh_api)
    print ("type_of_link", type_of_link)
    print ("link: ", link)
    if type_of_link == "pull request" or type_of_link == "issue":
        try:
            api = None
            headers = None
            timeline_data,user_dict  = github_issue_pull_fetch_data(CVE_ID,gh_api,api,headers,repo_slug, link, timeline_data,nvd_date_formatted, event_id, token,user_dict)
        except Exception as e:
            print("github_issue_pull_fetch_data is not working")
            pull_miss_dict = {'CVE_ID':[], 'link':[], "type":[]}
            pull_miss_dict['CVE_ID'].append(CVE_ID)
            pull_miss_dict['link'].append(link)
            pull_miss_dict['type'].append(type_of_link)
            pull_miss_dict_df = pd.DataFrame(pull_miss_dict)
            pull_miss_df = pd.read_csv("pull_miss_dict_df.csv")
            pull_miss_df = pull_miss_df.append(pull_miss_dict_df, ignore_index=True)
            pull_miss_df.to_csv("pull_miss_dict_df.csv", index=False)
            #raise (e)
            #return timeline_data,user_dict
            

    elif type_of_link == "commit":
        try:
            #CVE_ID, gh_api, user_name, repo_name, link, timeline_data, nvd_date_formatted, added_commit
            timeline_data,user_dict = github_commit_fetch_data(CVE_ID, gh_api, repo_slug, link, timeline_data, nvd_date_formatted, event_id,user_dict)
        except Exception as e:
            print("github_commit_fetch_data is not working")
            commits_miss_dict = {'CVE_ID':[], 'repo_slug':[],"commit_hash":[], "link":[], "role":[]}
            commits_miss_dict['CVE_ID'].append(CVE_ID)
            commits_miss_dict['repo_slug'].append(None)
            commits_miss_dict['commit_hash'].append(None)
            commits_miss_dict['link'].append(link)
            commits_miss_dict['role'].append("commit")              
            commits_miss_dict_df = pd.DataFrame(commits_miss_dict)
            commits_miss_df = pd.read_csv("commits_miss_dict_df.csv")
            commits_miss_df = commits_miss_df.append(commits_miss_dict_df, ignore_index=True)
            commits_miss_df.to_csv("commits_miss_dict_df.csv", index=False)
            #raise (e)
            #return timeline_data,user_dict
    else:
        other_links_dict = {"CVE_ID":[], "link":[]}
        other_links_dict['CVE_ID'].append(CVE_ID)
        other_links_dict['link'].append(link)
        other_links_dict_df = pd.DataFrame(other_links_dict)
        other_links_df = pd.read_csv("other_links.csv")
        other_links_df = other_links_df.append(other_links_dict_df, ignore_index=True)
        other_links_df.to_csv("other_links.csv", index=False)
        print ("type of link not recognized")
        print (link)
        #eturn timeline_data,user_dict

    #print ("end of main",timeline_data)
    print ("**********************")

    timeline_df = pd.DataFrame(timeline_data)
    output_data = pd.read_csv("output_data.csv")
    output_data = output_data.append(timeline_df, ignore_index=True)
    output_data.drop_duplicates(inplace=True)
    output_data.to_csv("output_data.csv", index=False)

    user_dict_df = pd.DataFrame(user_dict)
    user_df = pd.read_csv("user_data.csv")
    user_df.drop_duplicates(inplace=True)
    user_df = user_df.append(user_dict_df, ignore_index=True)
    user_df.to_csv("user_data.csv", index=False)

    return timeline_data,user_dict


