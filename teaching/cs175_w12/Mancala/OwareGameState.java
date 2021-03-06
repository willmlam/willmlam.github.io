/**
* The Mancala Game state class.
* Modified from code from http://electronicentertainment.wordpress.com/
* which in turn was modified from the Connect Four code by Alex Ihler
*/
import java.io.*;
import java.lang.Object;
import java.lang.Math;
import java.util.*;


public class OwareGameState extends MancalaGameState {

private final int ROW_SETTING = 2;
private final int COL_SETTING = 6;
private final int CAPLOW = 2;
private final int CAPHIGH = 3;

// Constructor
public OwareGameState(int startingStones) {
    super(startingStones);
    NUMROW = ROW_SETTING;
    NUMCOL = COL_SETTING;
    grid = new int[NUMROW][NUMCOL];
    reset();
}

public MancalaGameState copy() {
  MancalaGameState gs;
  gs = new OwareGameState(startingStones);
  gs.copyState(this);
  return gs;
}

// Check whether a given column constitutes a valid move
// If the opponent's pits are empty, must make a move that gives 
// the opponent stones
public boolean validMove(int col) { 
    if (col < 0 || col >= NUMCOL) return false;
    // Must make a move to give the other player seeds
    if (isEmptyRow(1-CurrentPlayer)) {
        if (CurrentPlayer == 0) {
            return grid[CurrentPlayer][col] >= NUMCOL - col;
        }
        else {
            return grid[CurrentPlayer][col] >= col + 1;
        }
    }
    else {
        // standard case
        return grid[CurrentPlayer][col] > 0;
    }
}

private boolean isEmptyRow(int row) {
    for (int i = 0; i < NUMCOL; ++i)
        if (grid[row][i] > 0) return false; 
    return true;
}

// Attempt to play a given column
// Cancel captures if the opponents pits would become empty
// Capture only when landing on opponents pits
// 
public MancalaGameState play(int col) throws Exception {
    if (!validMove(col)) throw new Exception("Invalid move!");
    int curRow = CurrentPlayer;
    int curCol = col;
    int startRow = curRow;
    int startCol = curCol;
    int stonesToMove = grid[curRow][curCol];
    grid[curRow][curCol] = 0;
    int curDirection = CurrentPlayer == 0 ? 1 : -1;
    while(stonesToMove-- > 0) {
        curCol += curDirection;
        if (curRow == startRow && curCol == startCol) {
            curCol += curDirection;
        }

        if (curCol >= NUMCOL) {
            curRow = 1;
            if (curRow == startRow && curCol - 1  == startCol) {
                curCol--;
                grid[curRow][--curCol] +=1;
            }
            else {
                grid[curRow][--curCol] +=1;
            }
            curDirection = -1;
        }
        else if (curCol < 0) {
            curRow = 0;
            if (curRow == startRow && curCol + 1  == startCol) {
                curCol++;
                grid[curRow][++curCol] +=1;
            }
            else {
                grid[curRow][++curCol] +=1;
            }
            curDirection = 1;
        }
        else {
            ++grid[curRow][curCol];
        }
        // Checking for captures
        if (stonesToMove == 0 && curRow == 1-CurrentPlayer) {
            boolean marked[] = new boolean[NUMCOL];
            for (int tempCol = curCol; tempCol >=0 && tempCol < NUMCOL; 
                    tempCol -= curDirection) {

                if (grid[curRow][tempCol] < CAPLOW || 
                        grid[curRow][tempCol] > CAPHIGH) {
                    break;
                }
                marked[tempCol] = true;
            }
            if (isCaptureGood(marked)) {
                for (int i = 0; i < NUMCOL; ++i) {
                    if (marked[i]) {
                        score[CurrentPlayer] += grid[1-CurrentPlayer][i];
                        grid[1-CurrentPlayer][i] = 0;
                    }
                }
            }
        }
    }
    CurrentPlayer = 1-CurrentPlayer;
    return this;
}

private boolean isCaptureGood(boolean marked[]) {
    for (int i = 0; i < NUMCOL; ++i)
        if (grid[1-CurrentPlayer][i] > 0 && !marked[i]) return true;
    return false;
}

// Check for terminal state
public boolean checkEndGame() {
    int scoreLimit = NUMROW*NUMCOL*startingStones / 2;
    if (score[0] > scoreLimit || score[1] > scoreLimit) {
        return true;
    }
    for (int i = 0; i < NUMCOL; ++i) {
        if (validMove(i)) return false;
    }
    return true;
}

public void computeFinalScore() {
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

