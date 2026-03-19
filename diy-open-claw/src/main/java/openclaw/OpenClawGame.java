package openclaw;

import javax.swing.JFrame;
import javax.swing.SwingUtilities;

/**
 * Entry point for the DIY Open Claw game.
 *
 * Run with:
 *   javac -d out src/main/java/openclaw/*.java
 *   java  -cp out openclaw.OpenClawGame
 *
 * Or simply:
 *   java src/main/java/openclaw/OpenClawGame.java   (single-file source launcher, JDK 14+)
 */
public class OpenClawGame {

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("🎮 DIY Open Claw");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setResizable(false);

            GamePanel panel = new GamePanel();
            panel.setPreferredSize(
                new java.awt.Dimension(GamePanel.WIDTH, GamePanel.HEIGHT)
            );
            frame.add(panel);
            frame.pack();
            frame.setLocationRelativeTo(null); // centre on screen
            frame.setVisible(true);
        });
    }
}
