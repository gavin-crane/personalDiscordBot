import wavelink
from discord.ext import commands
import re

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

        if vc.loop:
            return await vc.play(track)
        
        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await vc.play(next_song)
            await ctx.send(f"Now Playing: {next_song.title}")
            print("Next song: {next_song.title}")
               
    @commands.command(name='play', help='Searches given track on youtube')
    async def play(self,ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.author.voice:
            return await ctx.send("Join a channel first!", delete_after = 10)
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls = wavelink.Player) 
        else:
            vc: wavelink.Player = ctx.voice_client
        
        # Check if the input is a valid YouTube URL
        youtube_url = re.search("(?P<url>https?://)?(www\.)?(youtube\.com|youtu\.?be)/(watch\?v=)?(?P<id>[A-Za-z0-9\-=_]+)", search)
        
        if youtube_url:
            # Create a track object using the YouTube URL
            track = wavelink.YouTubeTrack(youtube_url.group("id"))
        else:
            track = wavelink.YouTubeTrack(search)
        
        if vc.is_playing():
            await vc.queue.put_wait(track)
            await ctx.send(f"Adding to queue: {search.title}")
             
        else:
            await ctx.send(f"Playing: {search.title}")
           
            await vc.play(track)
        vc.ctx = ctx
        setattr(vc, "loop", False)
        
    @commands.command(name='skip', help='Skips to next song if it exists')
    async def skip(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc:
            if not vc.queue.is_empty:
                next_song = vc.queue.get()
                await vc.play(next_song)
                await ctx.send("Skipped")
            else:
                await ctx.send("Nothing to skip!")
        else:
           await ctx.send("Thats illegal") 
    
    @commands.command(aliases=['dc'], name = 'disconnect', help = 'No arguments, disconnects bot and clears music queue. dc also works')
    async def disconnect(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc:
            if not vc.queue.is_empty:
                await vc.stop()
                vc.queue.clear()
                await vc.disconnect()
                await ctx.send(f"Disconnected and cleared queue")
            elif vc.is_playing():
                await vc.stop()
                await vc.disconnect()
                await ctx.send(f"Stopped song and disconnected")
            else:
                await vc.disconnect()
                await ctx.send(f"Disconnected")
        else:
            await ctx.send("Thats illegal")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))