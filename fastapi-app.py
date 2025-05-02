"""
Tournament Scheduler Web Application
"""

from fastapi import FastAPI, Request, File, UploadFile, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Dict, Optional
import pandas as pd
import io
import json
import os
from datetime import datetime
import uuid
from pydantic import BaseModel
import traceback

# Import the tournament scheduler
from scheduler import Person, Team, Match, Tournament

app = FastAPI(title="Tournament Scheduler")

# Configure templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for demo purposes (in production, use a database)
TOURNAMENTS = {}

class TeamModel(BaseModel):
    name: str
    trainer_name: str

class JudgeModel(BaseModel):
    name: str
    child_team: Optional[str] = None

class PlayerModel(BaseModel):
    name: str
    team: str
    parent_name: Optional[str] = None

class MatchModel(BaseModel):
    home_team: str
    away_team: str
    time: str  # Format: "YYYY-MM-DD HH:MM"
    location: str
    plan_number: int

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/tournaments", response_class=HTMLResponse)
async def list_tournaments(request: Request):
    return templates.TemplateResponse("tournaments.html", {
        "request": request,
        "tournaments": list(TOURNAMENTS.values())
    })

@app.get("/tournaments/{tournament_id}", response_class=HTMLResponse)
async def view_tournament(request: Request, tournament_id: str):
    if tournament_id not in TOURNAMENTS:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament_data = TOURNAMENTS[tournament_id]
    return templates.TemplateResponse("tournament_details.html", {
        "request": request,
        "tournament": tournament_data
    })

@app.post("/tournaments/create")
async def create_tournament(name: str = Form(...)):
    tournament_id = str(uuid.uuid4())
    TOURNAMENTS[tournament_id] = {
        "id": tournament_id,
        "name": name,
        "created_at": datetime.now().isoformat(),
        "teams": [],
        "judges": [],
        "players": [],
        "matches": [],
        "schedule": None
    }
    return RedirectResponse(url=f"/tournaments/{tournament_id}", status_code=303)

@app.post("/tournaments/{tournament_id}/upload-matches")
async def upload_matches(tournament_id: str, file: UploadFile = File(...)):
    if tournament_id not in TOURNAMENTS:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Process the file based on its type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Process match data (example - adjust based on your file format)
        matches = []
        for _, row in df.iterrows():
            try:
                match = {
                    "home_team": str(row.get("Home", "")),
                    "away_team": str(row.get("Away", "")),
                    "time": parse_time(row.get("Time", "")),
                    "location": str(row.get("Location", "")),
                    "plan_number": int(row.get("Plan", 0))
                }
                matches.append(match)
            except Exception as e:
                print(f"Error processing row: {row}, {str(e)}")
                continue
        
        # Update tournament data
        TOURNAMENTS[tournament_id]["matches"] = matches
        
        return RedirectResponse(url=f"/tournaments/{tournament_id}", status_code=303)
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/tournaments/{tournament_id}/add-team")
async def add_team(tournament_id: str, team: TeamModel):
    if tournament_id not in TOURNAMENTS:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    TOURNAMENTS[tournament_id]["teams"].append({
        "name": team.name,
        "trainer_name": team.trainer_name,
        "players": []
    })
    
    return {"success": True}

@app.post("/tournaments/{tournament_id}/add-judge")
async def add_judge(tournament_id: str, judge: JudgeModel):
    if tournament_id not in TOURNAMENTS:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    TOURNAMENTS[tournament_id]["judges"].append({
        "name": judge.name,
        "child_team": judge.child_team
    })
    
    return {"success": True}

@app.post("/tournaments/{tournament_id}/add-player")
async def add_player(tournament_id: str, player: PlayerModel):
    if tournament_id not in TOURNAMENTS:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    # Find the team
    team_found = False
    for team in TOURNAMENTS[tournament_id]["teams"]:
        if team["name"] == player.team:
            team["players"].append({
                "name": player.name,
                "parent_name": player.parent_name
            })
            team_found = True
            break
    
    if not team_found:
        raise HTTPException(status_code=404, detail=f"Team {player.team} not found")
    
    # Also add to players list
    TOURNAMENTS[tournament_id]["players"].append({
        "name": player.name,
        "team": player.team,
        "parent_name": player.parent_name
    })
    
    return {"success": True}

@app.post("/tournaments/{tournament_id}/generate-schedule")
async def generate_schedule(tournament_id: str):
    if tournament_id not in TOURNAMENTS:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament_data = TOURNAMENTS[tournament_id]
    
    try:
        # Create tournament object
        tournament = Tournament()
        
        # Add teams
        teams_dict = {}
        for team_data in tournament_data["teams"]:
            team = Team(team_data["name"])
            tournament.add_team(team)
            teams_dict[team.name] = team
            
            # Add trainer
            trainer = Person(team_data["trainer_name"], is_trainer=True)
            tournament.add_person(trainer)
            team.set_trainer(trainer)
        
        # Add players and connect to parents
        players_dict = {}
        for player_data in tournament_data["players"]:
            player = Person(player_data["name"])
            tournament.add_person(player)
            players_dict[player.name] = player
            
            # Add to team
            if player_data["team"] in teams_dict:
                teams_dict[player_data["team"]].add_player(player)
            
            # Connect to parent if applicable
            if player_data.get("parent_name"):
                # Find parent in trainers or judges
                parent = None
                for team in tournament_data["teams"]:
                    if team["trainer_name"] == player_data["parent_name"]:
                        for p in tournament.people:
                            if p.name == player_data["parent_name"]:
                                parent = p
                                break
                
                if not parent:
                    for judge_data in tournament_data["judges"]:
                        if judge_data["name"] == player_data["parent_name"]:
                            # Find or create judge
                            for p in tournament.people:
                                if p.name == player_data["parent_name"]:
                                    parent = p
                                    break
                            
                            if not parent:
                                parent = Person(player_data["parent_name"], is_judge=True)
                                tournament.add_person(parent)
                                tournament.add_judge(parent)
                
                if parent:
                    tournament.connect_parent_child(parent, player)
        
        # Add judges
        for judge_data in tournament_data["judges"]:
            # Check if judge already exists (might have been added as a parent)
            judge = None
            for p in tournament.people:
                if p.name == judge_data["name"]:
                    judge = p
                    break
            
            if not judge:
                judge = Person(judge_data["name"], is_judge=True)
                tournament.add_person(judge)
                tournament.add_judge(judge)
            
            # Connect to child's team if applicable
            if judge_data.get("child_team") and judge_data["child_team"] in teams_dict:
                # Find a player to set as child (simplified)
                for player in teams_dict[judge_data["child_team"]].players:
                    if not any(p.child == player for p in tournament.people if p.child):
                        tournament.connect_parent_child(judge, player)
                        break
        
        # Add matches
        for match_data in tournament_data["matches"]:
            # Get or create teams
            home_team = teams_dict.get(match_data["home_team"])
            if not home_team:
                home_team = Team(match_data["home_team"])
            
            away_team_name = match_data["away_team"]
            away_team = teams_dict.get(away_team_name)
            if not away_team:
                away_team = Team(away_team_name)
            
            # Parse time
            match_time = datetime.fromisoformat(match_data["time"])
            
            # Create match
            match = Match(
                home_team=home_team,
                away_team=away_team,
                time=match_time,
                location=match_data["location"],
                plan_number=match_data["plan_number"]
            )
            tournament.add_match(match)
        
        # Optimize judge assignments
        tournament.sort_matches_chronologically()
        judge_assignments = tournament.assign_judges_optimally()
        
        # Generate schedule
        schedule = tournament.generate_schedule_report()
        
        # Convert judge assignments to serializable format
        assignments = {}
        for judge, matches in judge_assignments.items():
            assignments[judge.name] = [
                {
                    "time": m.time.isoformat(),
                    "home_team": m.home_team.name,
                    "away_team": m.away_team.name,
                    "location": m.location,
                    "plan_number": m.plan_number
                }
                for m in matches
            ]
        
        # Update tournament data
        TOURNAMENTS[tournament_id]["schedule"] = {
            "report": schedule,
            "judge_assignments": assignments,
            "generated_at": datetime.now().isoformat()
        }
        
        return RedirectResponse(url=f"/tournaments/{tournament_id}", status_code=303)
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating schedule: {str(e)}")

def parse_time(time_str):
    """Parse time string into ISO format"""
    try:
        # For "YYYY-MM-DD HH:MM" format
        if isinstance(time_str, str) and len(time_str) > 5:
            return datetime.fromisoformat(time_str).isoformat()
        
        # For "HH:MM" format (assume today's date)
        elif isinstance(time_str, str) and ":" in time_str:
            hours, minutes = map(int, time_str.split(":"))
            dt = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            return dt.isoformat()
        
        # For float time (Excel time format)
        elif isinstance(time_str, float):
            hours = int(time_str * 24)
            minutes = int((time_str * 24 - hours) * 60)
            dt = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            return dt.isoformat()
        
        else:
            return datetime.now().isoformat()
    
    except Exception as e:
        print(f"Error parsing time: {time_str}, {str(e)}")
        return datetime.now().isoformat()

# Create directories if they don't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
