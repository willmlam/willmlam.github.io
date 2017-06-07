import java.io.BufferedReader;
import java.io.InputStreamReader;

public class interactive_Player implements MancalaPlayer
{
private int player;
private BufferedReader consoleInput;

public interactive_Player (int playerNum) {
  player = playerNum;
  consoleInput = new BufferedReader(new InputStreamReader(System.in));
}

public int getMove(MancalaGameState gs) throws Exception {
    return Integer.parseInt(consoleInput.readLine());
}

public Object postGameActions(MancalaGameState gs) {
    if (!gs.checkEndGame()) return null;

    // Make a copy to compute the final score
    MancalaGameState gsCopy = gs.copy();
    gsCopy.computeFinalScore();

    if (gsCopy.getScore(player) > gsCopy.getScore(1-player))
        System.out.println("You won!");
    else if (gsCopy.getScore(player) < gsCopy.getScore(1-player)) 
        System.out.println("You lost...");
    else 
        System.out.println("Game was a tie.");

    return null;
}

public Object actionsBeforeDeletion() {
    return null;
}

}
