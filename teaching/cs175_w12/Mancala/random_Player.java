import java.util.Random;
public class random_Player implements MancalaPlayer
{
private int player;

public random_Player (int playerNum) {
  player = playerNum;
}

public int getMove(MancalaGameState gs) throws Exception {
  MancalaGameState gs_copy=gs.copy();
  player = gs_copy.CurrentPlayer();
  Random generator = new Random();
  int move = -1;  

  for (int m=0;m<gs_copy.cols();m++) {
    if (gs_copy.validMove(m)) {
      if (move==-1) move=m;            // At least keep track of a valid move
      gs_copy.play(m);                    // Try playing that move on the current board
      if (gs_copy.checkEndGame()) {                //  If we win, definitely do that.
          gs_copy.computeFinalScore();
          if (gs_copy.getScore(player) > gs_copy.getScore(1-player)) {
              return m;   
          }
      } else {                         //  If it didn't win, "maybe" save it as our
        if (generator.nextInt(2)==0)   //   best move so far.
          move=m;
      }
    }
    gs_copy = gs.copy();
  }
  System.out.println(move);
  return move;   // Tell the game what our final decision is.
}

public Object postGameActions(MancalaGameState gs) {
    if (!gs.checkEndGame()) return null;

    // Make a copy to compute the final score
    MancalaGameState gsCopy = gs.copy();
    gsCopy.computeFinalScore();

    if (gsCopy.getScore(player) > gsCopy.getScore(1-player))
        System.out.println("I randomly win!");
    else if (gsCopy.getScore(player) < gsCopy.getScore(1-player)) 
        System.out.println("I randomly lost...");
    else 
        System.out.println("I randomly tied.");

    return null;
}

public Object actionsBeforeDeletion() {
    System.out.println("Performing actions before deletion.");
    return null;
}

}
