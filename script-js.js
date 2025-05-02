/**
 * Tournament Scheduler - Client-side JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle Add Team form submission
    const saveTeamBtn = document.getElementById('saveTeamBtn');
    if (saveTeamBtn) {
        saveTeamBtn.addEventListener('click', function() {
            const teamName = document.getElementById('teamName').value;
            const trainerName = document.getElementById('trainerName').value;
            
            if (!teamName || !trainerName) {
                alert('Please fill in all required fields');
                return;
            }
            
            // Get tournament ID from URL
            const pathSegments = window.location.pathname.split('/');
            const tournamentId = pathSegments[pathSegments.length - 1];
            
            fetch(`/tournaments/${tournamentId}/add-team`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: teamName,
                    trainer_name: trainerName
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal and refresh page
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addTeamModal'));
                    modal.hide();
                    window.location.reload();
                } else {
                    alert('Error adding team');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding team');
            });
        });
    }
    
    // Handle Add Judge form submission
    const saveJudgeBtn = document.getElementById('saveJudgeBtn');
    if (saveJudgeBtn) {
        saveJudgeBtn.addEventListener('click', function() {
            const judgeName = document.getElementById('judgeName').value;
            const judgeChildTeam = document.getElementById('judgeChildTeam').value;
            
            if (!judgeName) {
                alert('Please enter judge name');
                return;
            }
            
            // Get tournament ID from URL
            const pathSegments = window.location.pathname.split('/');
            const tournamentId = pathSegments[pathSegments.length - 1];
            
            fetch(`/tournaments/${tournamentId}/add-judge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: judgeName,
                    child_team: judgeChildTeam || null
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal and refresh page
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addJudgeModal'));
                    modal.hide();
                    window.location.reload();
                } else {
                    alert('Error adding judge');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding judge');
            });
        });
    }
    
    // Handle Add Player form submission
    const savePlayerBtn = document.getElementById('savePlayerBtn');
    if (savePlayerBtn) {
        savePlayerBtn.addEventListener('click', function() {
            const playerName = document.getElementById('playerName').value;
            const playerTeam = document.getElementById('playerTeam').value;
            const playerParent = document.getElementById('playerParent').value;
            
            if (!playerName || !playerTeam) {
                alert('Please fill in all required fields');
                return;
            }
            
            // Get tournament ID from URL
            const pathSegments = window.location.pathname.split('/');
            const tournamentId = pathSegments[pathSegments.length - 1];
            
            fetch(`/tournaments/${tournamentId}/add-player`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: playerName,
                    team: playerTeam,
                    parent_name: playerParent || null
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal and refresh page
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addPlayerModal'));
                    modal.hide();
                    window.location.reload();
                } else {
                    alert('Error adding player');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding player');
            });
        });
    }
    
    // Set team in Add Player modal
    const addPlayerModal = document.getElementById('addPlayerModal');
    if (addPlayerModal) {
        addPlayerModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            if (button) {
                const team = button.getAttribute('data-team');
                if (team) {
                    const teamSelect = document.getElementById('playerTeam');
                    if (teamSelect) {
                        for (let i = 0; i < teamSelect.options.length; i++) {
                            if (teamSelect.options[i].value === team) {
                                teamSelect.selectedIndex = i;
                                break;
                            }
                        }
                    }
                }
            }
        });
    }
});
