package net.ltecher.admin.bot;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.User;
import net.dv8tion.jda.api.events.interaction.command.CommandAutoCompleteInteractionEvent;
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import net.dv8tion.jda.api.interactions.commands.Command;

import java.awt.Color;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;


public class EventListener extends ListenerAdapter {
    public HashMap<User, ArrayList<String>> muted = new HashMap<User, ArrayList<String>>();
    
    @Override
    public void onSlashCommandInteraction(SlashCommandInteractionEvent event) {
        if (event.getGuild() == null) {
            return;
        }

        switch (event.getName()) {
            case "mute":
                User member = event.getOption("user").getAsUser();
                if (muted.containsKey(member) && muted.get(member).get(0) == (String)event.getGuild().getId()) {
                    muted.remove(member);

                    EmbedBuilder embed = new EmbedBuilder();
                    embed.setTitle("Success!", null);
                    embed.setColor(Color.GREEN);
                    
                    embed.setDescription("Successfully unmuted " + member.getAsMention() + "!");

                    event.reply("").setEmbeds(embed.build()).queue();
                    break;
                }

                EmbedBuilder embed = new EmbedBuilder();
                embed.setTitle("Success!", null);
                embed.setColor(Color.GREEN);
                
                String reason = "none";

                try {
                    reason = event.getOption("reason").getAsString();
                } catch (Exception e) {
                    
                }

                ArrayList<String> guild_reason = new ArrayList<String>();

                guild_reason.add(reason);
                guild_reason.add((String) event.getGuild().getId());

                muted.put(member, guild_reason);

                embed.setDescription("Successfully muted " + member.getAsMention() + " for reason " + reason + "!");

                event.reply("").setEmbeds(embed.build()).queue();
                
                break;
        }
    }
    public void onMessageReceived(MessageReceivedEvent event) {
        if (muted.containsKey(event.getAuthor())) {
            System.out.println(muted.get(event.getAuthor()).get(1) + " " + event.getGuild().getId());
            System.out.println((String)muted.get(event.getAuthor()).get(1) == (String)event.getGuild().getId());
            if ((String)muted.get(event.getAuthor()).get(1) == (String)event.getGuild().getId()) {
                EmbedBuilder embed = new EmbedBuilder();
                embed.setTitle("Muted!", null);
                embed.setColor(Color.RED);
                
                embed.setDescription(event.getAuthor().getAsMention() + ", You are muted for reason \"" + muted.get(event.getAuthor()).get(0) + "\" and cannot talk whilst muted!");
                
                event.getMessage().reply("").setEmbeds(embed.build()).queue();
                event.getMessage().delete().queue();
            }
        }
    }
    @Override
    public void onCommandAutoCompleteInteraction(CommandAutoCompleteInteractionEvent event) {
        List<net.dv8tion.jda.api.interactions.commands.Command.Choice> options = Stream.of(new String[]{"Rock", "Paper", "Sicours"})
            .filter(word -> word.startsWith(event.getFocusedOption().getValue())) // only display words that start with the user's current input
            .map(word -> new Command.Choice(word, word)) // map the words to choices
            .collect(Collectors.toList());
        event.replyChoices(options).queue();
    }
}
