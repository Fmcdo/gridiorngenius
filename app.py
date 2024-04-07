import os
import gradio as gr
from openai import OpenAI
from espn_api.football import League

client = OpenAI(api_key=os.environ['FantasyFootball'])

# Initialize the ESPN fantasy football league
league_id = 127350489
year = 2023
espn_s2 = 'AEAlA3qZu%2B6oT3o7iOVjKcvTxdY7WDYc5Z0PLZBYbioCe41IMuB%2Bs9%2FXKhjIenSpSoCgB2gQ%2F48AjUJf5acD4POxebPJ474fWmy4DEQx071jeiFext8FpJ9f5ujYnk%2BnnDeq14ZwSiQxpgrP7c%2Bmd1e%2FQXIwkZ8A6kOAdsQjZKfGcRTKO69qO%2Bt4xEwRKw1AI%2BggzCi%2F%2Beu6P5TJs1yS7L3QQv5HZXeIHYPTniX1VDENXb%2FZSnl0UWVkjk8rNN1BPO%2F8Dg313kHUG9WhOypzQgl9AAdJJE4PVHVJxxfQlOksow%3D%3D'
swid = '{8A8C7422-B6DE-497D-9157-458A1C638355}'
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)


def analyze_team(team):
    strengths = {}
    weaknesses = {}
    underperformers = []
    potential_pickups = []

    for player in team.roster:
        # Analyze strengths and weaknesses based on projected points
        if player.projected_total_points >= 15:
            strengths[player.position] = strengths.get(player.position, 0) + 1
        else:
            weaknesses[player.position] = weaknesses.get(player.position, 0) + 1

        # Identify underperforming players
        if player.avg_points < player.projected_avg_points and not player.injured:
            underperformers.append(player.name)

        # Identify potential waiver wire pickups based on ownership and starting percentages
        if player.percent_owned < 50 and player.percent_started < 50:
            potential_pickups.append(player.name)

    # Analysis of team's acquisition activities
    acquisition_analysis = {
        'acquisitions': team.acquisitions,
        'budget_spent': team.acquisition_budget_spent,
        'trades': team.trades
    }

    return strengths, weaknesses, underperformers, potential_pickups, acquisition_analysis

def generate_team_summary_with_openai(team_name, league):
    for team in league.teams:
        if team.team_name == team_name:
            strengths, weaknesses, underperformers, potential_pickups, acquisition_analysis = analyze_team(team)

            prompt = f"Team {team_name} analysis:\n"
            if underperformers:
                prompt += f"- Underperforming players: {', '.join(underperformers)}\n"
            if potential_pickups:
                prompt += f"- Potential waiver wire pickups (undervalued players): {', '.join(potential_pickups)}\n"
            prompt += f"- Acquisition activity: {acquisition_analysis['acquisitions']} acquisitions, {acquisition_analysis['budget_spent']} budget spent, {acquisition_analysis['trades']} trades.\n"
            prompt += "Based on this analysis, provide detailed recommendations for lineup changes, potential trades, or waiver wire pickups."

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            recommendations = response.choices[0].message.content.strip()
            return recommendations
    return "Team not found. Please ensure you've entered the correct team name."


def gradio_interface(team_name):
    return generate_team_summary_with_openai(team_name, league)

iface = gr.Interface(fn=gradio_interface, inputs="text", outputs="text", description="Enter your Fantasy Football Team Name to get recommendations:")
iface.launch()
