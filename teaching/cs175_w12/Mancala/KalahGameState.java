/**
* The Mancala Game state class.
* Modified from code from http://electronicentertainment.wordpress.com/
* which in turn was modified from the Connect Four code by Alex Ihler
*/
import java.io.*;
import java.lang.Object;
import java.lang.Math;
import java.util.*;


public class KalahGameState extends MancalaGameState {

private final int ROW_SETTING = 2;
private final int COL_SETTING = 6;

// Constructor
public KalahGameState(int startingStones) {
    super(startingStones);
    NUMROW = ROW_SETTING;
    NUMCOL = COL_SETTING;
    grid = new int[NUMROW][NUMCOL];
    reset();
}

public MancalaGameState copy() {
  MancalaGameState gs;
  gs = new KalahGameState(startingStones);
  gs.copyState(this);
  return gs;
}

// Check whether a given column constitutes a valid move
public boolean validMove(int col) { 
    return (col>=0 && col < NUMCOL && grid[CurrentPlayer][col] > 0); 
}

// Attempt to play a given column
public MancalaGameState play(int col) throws Exception {
  if (!validMove(col)) throw new Exception("Invalid move!");
  int curRow = CurrentPlayer; 
  int curCol = col; 
  int stonesToMove = grid[curRow][curCol];
  grid[curRow][curCol] = 0;
  int curDirection = CurrentPlayer == 0 ? 1 : -1;
  boolean bonusTurn = false;
  while(stonesToMove-- > 0) {
    curCol += curDirection; 
    if (curCol >= NUMCOL) {
        curRow = 1;
        if (CurrentPlayer == 0) {
            score[0] += 1;
            if (stonesToMove == 0) bonusTurn = true;
        }
        else {
            grid[curRow][--curCol] += 1;
        }
        curDirection = -1;
    }
    else if (curCol < 0) {
        curRow = 0;
        if (CurrentPlayer == 1) {
            score[1] += 1;
            if (stonesToMove == 0) bonusTurn = true;
        }
        else {
            grid[curRow][++curCol] += 1;
        }
        curDirection = 1;
    }
    else {
        ++grid[curRow][curCol];
    }

    // grab conditions?
    if (curCol >= 0 && curCol < NUMCOL && 
        grid[curRow][curCol] == 1 && stonesToMove == 0) {
        if (curRow == 0 && curRow == CurrentPlayer && grid[1][curCol] > 0) {
            int grabAmt = grid[1][curCol] + 1;
            score[CurrentPlayer] += grabAmt;
            grid[1][curCol] = 0;
            grid[0][curCol] = 0;
        }
        else if (curRow == 1 && curRow == CurrentPlayer && grid[0][curCol] > 0) {
            int grabAmt = grid[0][curCol] + 1;
            score[CurrentPlayer] += grabAmt;
            grid[0][curCol] = 0;
            grid[1][curCol] = 0;
        }
    }
  }

  if (!bonusTurn)
      CurrentPlayer = 1-CurrentPlayer;                     // swap players
	return this;
}

// Check for terminal state
public boolean checkEndGame(){
    boolean end0 = true;
    for (int i=0; i < NUMCOL; ++i) {
        if (grid[0][i] != 0) {
            end0 = false;
            break;
        }
    }
    boolean end1 = true;
    for (int i=0; i < NUMCOL; ++i) {
        if (grid[1][i] != 0) {
            end1 = false;
            break;
        }
    }
    return end0 || end1;
}

public void computeFinalScore() {
    if (!checkEndGame()) return;
    if (finalScoresComputed) return;
    for (int i=0; i < NUMCOL; ++i) { 
        score[0] += grid[0][i];
        grid[0][i] = 0;
    }
    for (int i=0; i < NUMCOL; ++i) { 
        score[1] += grid[1][i];
        grid[1][i] = 0;
    }
    finalScoresComputed = true;
}

public void printState() {
    for (int i = 1; i >= 0; --i) {
        if (i == 1) 
            System.out.print(" " + i + "| " + score[i] + " \t");
        else        
            System.out.print(" " + i + "|   \t");
        for (int j = 0; j < NUMCOL; ++j) {
            System.out.print(" " + grid[i][j]);
        }
        if (i == 0) 
            System.out.print(" \t" + score[i]);
        System.out.println();
    }
    System.out.println("--------------------------");
    System.out.println("         0 1 2 3 4 5");
}

}

