/**
* The Mancala Game state class.
* Modified from code from http://electronicentertainment.wordpress.com/
* which in turn was modified from the Connect Four code by Alex Ihler
*/
import java.io.*;
import java.lang.Object;
import java.lang.Math;
import java.util.*;

abstract class MancalaGameState {

protected final int EMPTY = -1;
protected final int NUMPLAYER = 2;  // # of players
protected int NUMROW;
protected int NUMCOL;      

protected int startingStones;
protected int CurrentPlayer;      // identifies the current player
protected int grid[][];           // represents the grid of the game board

protected int score[];
protected boolean finalScoresComputed;

// Constructor:  Mancala
public MancalaGameState(int startingStones) {
  this.startingStones = startingStones;
  score = new int [NUMPLAYER];
}

// Copy the board state before modifying
public abstract MancalaGameState copy();

protected void copyState(MancalaGameState orig) {
  for (int i=0;i<NUMROW;i++) for (int j=0;j<NUMCOL;j++) grid[i][j]=orig.grid[i][j];
  score[0] = orig.score[0];
  score[1] = orig.score[1];
  finalScoresComputed = orig.finalScoresComputed;
  CurrentPlayer=orig.CurrentPlayer;
}

// Wipe board and start over
public void reset() {
  for(int i = 0; i < NUMROW; i++)
    for(int j = 0; j < NUMCOL; j++)
      grid[i][j] = startingStones;
  score[0] = 0;
  score[1] = 0;
  finalScoresComputed = false;
  CurrentPlayer = 0;
}

// Accessor functions
public int CurrentPlayer() { return CurrentPlayer; }  // which player is up next?
public int stonesAt(int x,int y) { return grid[x][y]; } 
public int rows() { return NUMROW; }                // get the board size
public int cols() { return NUMCOL; }                //
public int getScore(int i) { return score[i]; }

// Check whether a given column constitutes a valid move
public abstract boolean validMove(int col);

// Attempt to play a given column
public abstract MancalaGameState play(int col) throws Exception;

// Check for terminal state
public abstract boolean checkEndGame();

public abstract void computeFinalScore();

public abstract void printState();

}

