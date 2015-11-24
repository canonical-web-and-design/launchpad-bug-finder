#!/usr/bin/python

# System dependencies
import argparse
import sys
from datetime import datetime, timedelta, tzinfo

# Modules
from launchpadlib.launchpad import Launchpad


# Parse arguments passed to this script
class _UTC(tzinfo):
    """
    A tzinfo class for adding the UTC timezone to datetime objects
    E.g.:
        datetime_object.replace(tzinfo=_UTC())
    """

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return timedelta(0)

UTC = _UTC()

parser = argparse.ArgumentParser(
    'Generate a report of bugs closed in a date range'
)
parser.add_argument('start', metavar='START', type=str,
                    help='Start date of the form YYYY-MM-DD')
parser.add_argument('end', metavar='END', type=str,
                    help='End date off the form YYYY-MM-DD')
args = parser.parse_args()
try:
    start = datetime.strptime(args.start, '%Y-%m-%d')
except ValueError:
    parser.print_help()
    sys.exit(1)
start = start.replace(tzinfo=UTC)
try:
    end = datetime.strptime(args.end, '%Y-%m-%d')
except ValueError:
    parser.print_help()
    sys.exit(1)
end += timedelta(hours=23, minutes=59, seconds=59)
end = end.replace(tzinfo=UTC)


# Collect statuses into categories
fixed = ['Fix Released', 'Fix Committed']
invalid = ['Incomplete', 'Invalid', 'Won\'t Fix', 'Opinion']
new = ['New', 'Triaged', 'Confirmed']
allStatus = [
    'Fix Released', 'Fix Committed', 'Incomplete', 'Invalid',
    'Won\'t Fix', 'Opinion', 'New', 'Triaged', 'Confirmed'
]

# Setup Launchpad object
launchpad = Launchpad.login_with('Canonical web team stats', 'production')
project = launchpad.projects['ubuntu-ux']

# Prepare the other settings variables for the script
proj_list = ['ubuntu-ux']
formatted_start = start.strftime('%A, %B %e, %Y')
formatted_end = end.strftime('%A, %B %e, %Y')
count = 0
grandtotal = 0
group = 'unity-design-team'
membercount = 0

# Start running the script
# ==
print 'Bugs fixed between %s and %s:' % (formatted_start, formatted_end)

# Run for each project in the list
# ==
for proj_name in proj_list:
    # Get this project
    print
    print 'Project: ' + proj_name
    project = launchpad.projects[proj_name]

    # Get all bugs for this project
    bugTasks = project.searchTasks(status=allStatus)
    print "Total number of bugs: " + str(len(bugTasks))

    # Get new bugs
    bugs = [
        bug for bug in project.searchTasks(status="New")
        if bug.date_created and end >= bug.date_created >= start
    ]
    print 'New bugs:'
    if len(bugs) > 0:
        for bug in bugs:
            count += 1
            print bug.title.encode('utf-8').strip()
        print 'Total: ' + str(count)
        grandtotal += count
        count = 0
    else:
        print 'Total: ' + str(count)

    # Get fixed bugs
    bugs = [
        bug for bug in project.searchTasks(status=fixed)
        if bug.date_closed and end >= bug.date_closed >= start
    ]
    print 'Bugs fixed'
    if len(bugs) > 0:
        for bug in bugs:
            count += 1
            print bug.title.encode('utf-8').strip()
        print 'Total: ' + str(count)
        grandtotal += count
        count = 0
    else:
        print 'Total: ' + str(count)

    # Get "invalid" bugs
    bugs = [
        bug for bug in project.searchTasks(status=invalid)
        if bug.date_closed and end >= bug.date_closed >= start
    ]
    print
    print 'Bugs marked as invalid'
    if len(bugs) > 0:
        for bug in bugs:
            count += 1
            print bug.title.encode('utf-8').strip()
        print 'Total: ' + str(count)
        grandtotal += count
        count = 0
    else:
        print 'Total: ' + str(count)

print
print 'Grand Total: ' + str(grandtotal)

# Get bugs by members of the group
# ==
print 'Members of %s:' % (group)

proj_group = launchpad.people[group]
members = proj_group.members_details

if len(members) > 0:
    for person in members:
        membercount += 1

        # All bugs for this person
        memberBugs = project.searchTasks(
            assignee=person.member,
            status=allStatus
        )

        # Filter by date range
        memberBugsByRange = [
            bug for bug in memberBugs
            if bug.date_assigned and end >= bug.date_assigned >= start
        ]

        # Get fixed bugs for this person
        fixedBugs = project.searchTasks(assignee=person.member, status=fixed)
        fixedBugsByRange = [
            bug for bug in fixedBugs
            if bug.date_closed and end >= bug.date_closed >= start
        ]

        # Get new bugs for this person
        newBugs = project.searchTasks(assignee=person.member, status=new)
        newBugsByRange = [
            bug for bug in newBugs
            if bug.date_assigned and end >= bug.date_assigned >= start
        ]

        # Print all info about this person's bugs
        print (
            person.member.display_name + ' Total: '
            + str(len(memberBugsByRange)) + ' New: ' + str(len(newBugsByRange))
            + ' Fixed: ' + str(len(fixedBugsByRange))
        )
