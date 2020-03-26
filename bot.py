import os
import asyncio
from mcrcon import MCRcon
from discord.ext import commands
# from dotenv import load_dotenv
# load_dotenv()
import time

# TODO Commenting

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MC_SERVER_IP = os.getenv('MC_SERVER_IP')
MC_RCON_PORT = os.getenv('MC_RCON_PORT')
MC_RCON_PASS = os.getenv('MC_RCON_PASS')

bot = commands.Bot(command_prefix='!')
difficulty_array = ['easy', 'normal', 'hard']

proposals = list()

mcrcon = MCRcon(str(MC_SERVER_IP), str(MC_RCON_PASS))
mcrcon.connect()
print(mcrcon)
if not mcrcon:
    print('Password incorrect')
    exit(1)


CURRENT_ID = 0

class Proposal():
    def __init__(self, ctx, description='', description_args=[]):
        global CURRENT_ID
        self.id = CURRENT_ID
        CURRENT_ID += 1
        self.ctx = ctx
        self.proposer = ctx.author.name
        self.description = description.format(description_args)
        
        self.votes_for = [ctx.author]
        self.votes_against = []
        self.timeout = 600

    def do_task(self):
        pass
    
    async def compelete_execution(self):
        if len(self.votes_for) > len(self.votes_against):
            self.do_task()
            await self.ctx.send("{} - Passed".format(str(self)))
        else:
            await self.ctx.send("{} - Failed".format(str(self)))
        proposals.remove(self)
    
    def vote_for(self, voter):
        self.remove_vote(voter)
        self.votes_for.append(voter)
    
    def vote_against(self, voter):
        self.remove_vote(voter)
        self.votes_against.append(voter)

    def remove_vote(self, voter):
        if self.votes_against.__contains__(voter):
            self.votes_against.remove(voter)
        elif self.votes_for.__contains__(voter):
            self.votes_for.remove(voter)
    
    def get_voters(self):
        formatted_for = ', '.join(voter.name for voter in self.votes_for)
        formatted_against = ', '.join(voter.name for voter in self.votes_against)

        return "Votes for: {}\nVoters: {}\nVotes Against: {}\nVoters: {}\n".format(
            len(self.votes_for), formatted_for, len(self.votes_against), formatted_against
        )
    
    def __str__(self):
        return "#{}: {} Proposed {} - Time Remaining: {}".format(
            self.id, self.proposer, self.description, self.timeout
        )

    async def tick(self):
        while(1):
            await asyncio.sleep(1)
            print("Tick: {}".format(self.timeout))
            if self.timeout <= 0:
                await self.compelete_execution()
                return
            elif self.timeout == 60:
                await self.ctx.send("One minute left on proposal #{}".format(self.id))
                self.timeout -= 1
            else:
                self.timeout -= 1


class DifficultyProposal(Proposal):
    def __init__(self, ctx, difficulty):
        super().__init__(ctx, description='to set the difficulty to {0}', 
            description_args=difficulty)
        self.difficulty = difficulty
    
    def do_task(self):
        change_difficulty(self.difficulty)


def announce(message):
    command = "say {}".format(message)
    mcrcon.command(command)

def check_difficulty():
    difficulty = mcrcon.command('difficulty')
    print(difficulty)
    difficulty = difficulty.split(' ')
    return difficulty[3].lower()

def change_difficulty(difficulty):
    print('Changing difficulty')
    mcrcon.command("difficulty {}".format(difficulty))

@bot.command(name='info', help='Lists all pending proposals')
async def info(ctx):
    await ctx.send("Active Proposals: {}".format(', \n'.join(str(proposal) for proposal in proposals)))

@bot.command(name='vote', help='Casts a vote for a specified proposal')
async def vote(ctx, proposal_id: int, vote: str):
    print("id: {}, vote: {}".format(proposal_id, vote))
    for proposal in proposals:
        if proposal_id == proposal.id:
            print('found proposal')
            if vote.lower() == 'yes':
                print('yes')
                proposal.vote_for(ctx.author)
                await ctx.send(proposal.get_voters())
            elif vote.lower() == 'no':
                print('no')
                proposal.vote_against(ctx.author)
                await ctx.send(proposal.get_voters())
            else:
                await ctx.send("Vote must either be 'yes' or 'no'")

@bot.command(name='propose', help='Create a new proposal to vote on')
async def propose_difficulty(ctx, proposal_type: str, arg: str):
    if proposal_type == 'difficulty':
        if difficulty_array.__contains__(arg):
            if check_difficulty() != arg:
                proposal = DifficultyProposal(ctx, arg)
                proposals.append(proposal)
                await ctx.send(str(proposal))
                await proposal.tick()
            else:
                await ctx.send("The server is already at that difficulty")
        else:
            await ctx.send("Not a vaild difficulty :(")

@bot.command(name='command', help='Runs command on server')
@commands.has_role('server_admin')
async def command(ctx, *args):
    command = " ".join(args[:])
    resp = mcrcon.command(command)
    await ctx.send(resp)

@bot.command(name='zzz', help='Sets time to day if night')
@commands.has_role('server_admin')
async def zzz(ctx):
    time_data = mcrcon.command('time')
    time_data = time_data.split('\n')
    time_data = time_data[0]
    time_data = time_data.split()
    time_data = time_data[6]
    time_data = time_data[4:-2]
    current_time = time_data
    time_data = time_data.split(':')
    time_data = int(time_data[0])*100 + int(time_data[1])
    if time_data < 600 or time_data > 2000:
        print('Setting time to day')
        mcrcon.command('time set day')
        await ctx.send("Wakey Wakey!")
    else:
        await ctx.send("It isn't night time yet, the time is: {}".format(current_time))

@bot.command(name='share', help='Share the message with anyone on the server')
async def share(ctx, *args):
    message = " ".join(args[:])
    print(message)
    command = 'say <{}>: {}'.format(ctx.author.name, message)
    mcrcon.command(command)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    
if __name__ == "__main__":
    bot.run(TOKEN)