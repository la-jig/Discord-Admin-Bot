package net.ltecher.admin.bot;

import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.Permission;
import net.dv8tion.jda.api.entities.Activity;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import net.dv8tion.jda.api.interactions.commands.DefaultMemberPermissions;
import net.dv8tion.jda.api.interactions.commands.OptionType;
import net.dv8tion.jda.api.interactions.commands.build.Commands;
import net.dv8tion.jda.api.interactions.commands.build.OptionData;
import net.dv8tion.jda.api.requests.restaction.CommandListUpdateAction;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.logging.Logger;

public class Main extends ListenerAdapter {
    public static Logger LOGGER = Logger.getLogger("Discord Admin Bot");
    public static JDA client;

    public static void main(String[] args) throws FileNotFoundException {
        Scanner scanner = new Scanner(new File("token.txt"));
        String token = "";

        while (scanner.hasNextLine()) {
            token += scanner.nextLine();
        }

        JDABuilder builder = JDABuilder.createDefault(token);

        builder.setActivity(Activity.playing("Type /help for more info!"));
        builder.addEventListeners(new EventListener());

        try {
            LOGGER.info("Logging in...");
            client = builder.build();
        } catch (Exception e) {
            LOGGER.severe("Failed to start the bot: " + e.getClass() + e.getMessage());
            System.exit(1);
        }

        CommandListUpdateAction commands = client.updateCommands();

        commands.addCommands(
            Commands.slash("mute", "Mute/Unmute a user")
                .addOptions(new OptionData(OptionType.USER, "user", "User to mute")
                    .setRequired(true))
                .addOptions(new OptionData(OptionType.STRING, "reason", "The reason to mute (default: none)")
                    .setRequired(false))
                .setDefaultPermissions(DefaultMemberPermissions.enabledFor(Permission.MESSAGE_MANAGE))
                .setGuildOnly(true));
            Commands.slash("rps", "Play a game of rock paper sissours")
                .addOptions(new OptionData(OptionType.STRING, "choice", "Your choice")
                    .setRequired(true)
                .setAutoComplete(true));

        commands.queue();
    }
}