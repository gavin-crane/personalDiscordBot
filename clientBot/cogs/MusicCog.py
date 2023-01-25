import wavelink
from discord.ext import commands
import discord
import re

url_rx = re.compile(r'https?://(?:www\.)?.+') # for checking if input is a youtube link

class MusicCog(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        print("added music cog")
        self.bot = bot
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        # await wavelink.NodePool.create_node(bot=self.bot,
        #                                     host='lava.link',
        #                                     port=80,
        #                                     password='dismusic')
        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='purr.aikomechawaii.live',
                                            port=10415 ,
                                            password='AnythingAsPassword',
                                            https=False,
                                            region = 'us_west')
        
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        
        ctx = player.ctx
        vc: player = ctx.voice_client
        
        print(f"track end invoked! here is the queue{vc.queue}")

        if vc.loop:
            return await vc.play(track)
        
        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await vc.play(next_song)
            
            embed = discord.Embed(color=discord.Color.blurple())
            embed.title = "Now Playing:"
            embed.description = next_song.title
            
            await ctx.send(embed=embed)
            print("Next song: {next_song.title}")
               
    @commands.command(name='play', help='Searches given track on youtube, if a song is currently playing, it gets added to the queue')
    async def play(self,ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.author.voice:
            return await ctx.send("Join a channel first!", delete_after = 10)
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls = wavelink.Player) 
        else:
            vc: wavelink.Player = ctx.voice_client
        
        # Check if the input is a valid YouTube URL
        if not url_rx.match(str(search)):
            track = search
        else:
            track = f'ytsearch:{search}'
            
        embed = discord.Embed(color=discord.Color.blurple())    
             
        if vc.is_playing():
            vc.queue.put(track)
            embed.title = "Added to queue:"
            embed.description = search.title
            await ctx.send(embed=embed)
             
        else:
            embed.title = "Playing:"
            embed.description = search.title
            await ctx.send(embed=embed)
           
            await vc.play(track)
        vc.ctx = ctx
        setattr(vc, "loop", False)
        
    @commands.command(name='skip', help='Skips to next song if it exists')
    async def skip(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc:
            if not vc.queue.is_empty:
                print(f'skip invoked! Here is the queue {vc.queue}')
                print(f'is the queue after removing the skipped song: {vc.queue}')
                await vc.stop()
                await ctx.send("Skipped")
            else:
                await ctx.send("Nothing to skip!", delete_after=10)
        else:
           await ctx.send("Thats illegal", delete_after = 10)
    
    @commands.command(name = 'pause', help= 'pauses current song')
    async def pause(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("I am not currently playing anything!", delete_after=10)
        await vc.pause()
        await ctx.send("Paused the current track.")
            
    @commands.command(aliases=['res'], name = 'resume', help= 'resumes the track')
    async def resume(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if not vc:
            return await ctx.send("Illegal", delete_after=10)
        elif vc.is_paused():
            await vc.resume()
            await ctx.send("Resumed the current track.")
        else:
            await ctx.send("I am playing something right now!", delete_after=10)
         
    @commands.command(aliases=['dc'], name = 'disconnect', help = 'No arguments, disconnects bot and clears music queue. dc also works')
    async def disconnect(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc:
            if not vc.queue.is_empty:
                await vc.stop()
                vc.queue.clear()
                await vc.disconnect()
                await ctx.send(f"Disconnected and cleared queue", delete_after=10)
            elif vc.is_playing():
                await vc.stop()
                await vc.disconnect()
                await ctx.send(f"Stopped song and disconnected", delete_after=10)
            else:
                await vc.disconnect()
                await ctx.send(f"Disconnected")
        else:
            await ctx.send("Thats illegal", delete_after = 10)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))