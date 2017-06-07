interface MancalaPlayer
{

public int getMove(MancalaGameState gs) throws Exception;

// A general method that allows the class to do something based on 
// the final game state. Simply implement it as // "return null;" 
// if you are not using this.
// This should be called immediately after a game ends and before 
// computeFinalScore() is called on the game state.
public Object postGameActions(MancalaGameState gs);

// Similar to the above method, but should be called when objects 
// are about to lose their references. Used primarily to write data
// to disk once without being wasteful by using postGameActions.
public Object actionsBeforeDeletion();
}

