"""
Tournament Scheduler - Core scheduling logic
"""

import random
from collections import defaultdict
import datetime
from typing import List, Dict, Tuple, Set, Optional
import itertools

class Person:
    def __init__(self, name: str, is_trainer: bool = False, is_judge: bool = False):
        self.name = name
        self.is_trainer = is_trainer
        self.is_judge = is_judge
        self.child = None  # Reference to their child (Person object)
        self.team = None   # Team they belong to or coach

    def __str__(self):
        return f"{self.name}"

class Team:
    def __init__(self, name: str):
        self.name = name
        self.trainer = None  # Reference to the trainer (Person object)
        self.players = []    # List of Person objects

    def add_player(self, player: Person):
        self.players.append(player)
        player.team = self

    def set_trainer(self, trainer: Person):
        self.trainer = trainer
        trainer.is_trainer = True
        trainer.team = self

    def __str__(self):
        return self.name

class Match:
    def __init__(self, home_team: Team, away_team: Team, 
                 time: datetime.datetime, location: str, plan_number: int):
        self.home_team = home_team
        self.away_team = away_team
        self.time = time
        self.location = location
        self.plan_number = plan_number
        self.assigned_judge = None

    def is_home_match(self, team: Team) -> bool:
        return team == self.home_team

    def involves_team(self, team: Team) -> bool:
        return team == self.home_team or team == self.away_team

    def __str__(self):
        judge_str = f", Judge: {self.assigned_judge}" if self.assigned_judge else ""
        return f"{self.time.strftime('%H:%M')} - {self.home_team} vs {self.away_team} @ {self.location}{judge_str}"

class Tournament:
    def __init__(self):
        self.teams = []
        self.judges = []
        self.matches = []
        self.people = []

    def add_team(self, team: Team):
        self.teams.append(team)

    def add_judge(self, person: Person):
        person.is_judge = True
        self.judges.append(person)

    def add_match(self, match: Match):
        self.matches.append(match)

    def add_person(self, person: Person):
        self.people.append(person)

    def connect_parent_child(self, parent: Person, child: Person):
        parent.child = child

    def sort_matches_chronologically(self):
        """Sort matches by time to make scheduling easier"""
        self.matches.sort(key=lambda x: x.time)

    def get_home_matches(self) -> List[Match]:
        """Get all matches where one of our teams is the home team"""
        return [match for match in self.matches 
                if any(match.is_home_match(team) for team in self.teams)]

    def assign_judges_optimally(self):
        """
        Assign judges to home matches with the following priorities:
        1. Judges prefer to judge games with their children
        2. Even workload distribution
        3. Minimize time at venue for each judge
        """
        home_matches = self.get_home_matches()
        
        # Sort matches by time for sequential assignment
        home_matches.sort(key=lambda x: x.time)
        
        # Track assignments per judge
        judge_assignments = {judge: [] for judge in self.judges}
        
        # Group matches by time slot to handle concurrent games
        matches_by_time = defaultdict(list)
        for match in home_matches:
            matches_by_time[match.time].append(match)
        
        # First pass: assign judges to matches with their children
        for time, concurrent_matches in matches_by_time.items():
            for match in concurrent_matches:
                for judge in self.judges:
                    # If judge has a child and the child's team is playing in this match
                    if (judge.child and 
                        (judge.child.team == match.home_team or judge.child.team == match.away_team) and
                        not any(m.assigned_judge == judge for time_slot in matches_by_time.values() 
                               for m in time_slot if m.time == time)):
                        match.assigned_judge = judge
                        judge_assignments[judge].append(match)
                        break
        
        # Second pass: assign remaining matches to minimize time at venue and balance workload
        for time, concurrent_matches in sorted(matches_by_time.items()):
            unassigned_matches = [m for m in concurrent_matches if m.assigned_judge is None]
            
            if not unassigned_matches:
                continue
                
            # Sort judges by number of assignments (for balancing)
            sorted_judges = sorted(self.judges, key=lambda j: len(judge_assignments[j]))
            
            for match in unassigned_matches:
                # Find judges already at the venue at this time
                judges_present = {m.assigned_judge for time_slot in matches_by_time.values() 
                                for m in time_slot if m.time == time and m.assigned_judge is not None}
                
                # Prioritize judges already present, then those with fewer assignments
                candidate_judges = [j for j in sorted_judges if j not in judges_present 
                                   and not any(m.assigned_judge == j for m in concurrent_matches)]
                
                if not candidate_judges:
                    # If no available judges, take any judge with the smallest workload
                    candidate_judges = sorted_judges
                
                # Assign to judge with minimum workload
                best_judge = min(candidate_judges, key=lambda j: len(judge_assignments[j]))
                match.assigned_judge = best_judge
                judge_assignments[best_judge].append(match)
        
        # Return summary of assignments
        return judge_assignments

    def generate_schedule_report(self) -> str:
        """Generate a human-readable schedule with judge assignments"""
        report = "TOURNAMENT SCHEDULE\n"
        report += "==================\n\n"
        
        # Group matches by date
        matches_by_date = defaultdict(list)
        for match in self.matches:
            date_str = match.time.strftime('%Y-%m-%d')
            matches_by_date[date_str].append(match)
        
        # Print schedule by date
        for date, day_matches in sorted(matches_by_date.items()):
            report += f"Date: {date}\n"
            report += "-" * 50 + "\n"
            
            # Sort by time
            day_matches.sort(key=lambda m: m.time)
            
            for match in day_matches:
                time_str = match.time.strftime('%H:%M')
                judge_str = f"Judge: {match.assigned_judge}" if match.assigned_judge else "No judge assigned"
                report += f"{time_str} - Plan {match.plan_number} - {match.home_team} vs {match.away_team} @ {match.location} - {judge_str}\n"
            
            report += "\n"
        
        # Add judge workload summary
        report += "JUDGE ASSIGNMENTS\n"
        report += "=================\n\n"
        
        judge_assignments = defaultdict(list)
        for match in self.matches:
            if match.assigned_judge:
                judge_assignments[match.assigned_judge].append(match)
        
        for judge, assignments in judge_assignments.items():
            report += f"Judge: {judge}\n"
            report += f"Total assignments: {len(assignments)}\n"
            assignments.sort(key=lambda m: m.time)
            
            for match in assignments:
                time_str = match.time.strftime('%H:%M')
                report += f"  {time_str} - {match.home_team} vs {match.away_team} @ {match.location}\n"
            
            report += "\n"
        
        return report

    def import_from_csv(self, csv_data: str):
        """Import match data from CSV format"""
        # Implementation would depend on the specific CSV format
        pass  
