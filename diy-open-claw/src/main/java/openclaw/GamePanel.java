package openclaw;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import javax.swing.JPanel;
import javax.swing.Timer;

/**
 * The main game panel – owns the game loop, input handling, and rendering.
 *
 * Layout (all in pixels, 600 × 500 default):
 *   ┌──────────────────────────────────────┐
 *   │  ═══════ rail ═══════                │  y = 30
 *   │        ┃                              │
 *   │       [claw]                          │
 *   │                                       │
 *   │  ┌───── pit (prizes) ─────────┐      │  y = 300
 *   │  │  ●  ●    ●   ●  ●         │      │
 *   │  └────────────────────────────┘      │  y = 460
 *   │   Score: 0    Tries left: 3          │
 *   └──────────────────────────────────────┘
 */
public class GamePanel extends JPanel implements ActionListener {

    // ── Constants ────────────────────────────────────────────────────
    static final int WIDTH = 600;
    static final int HEIGHT = 500;

    private static final int RAIL_Y = 30;
    private static final int PIT_TOP = 300;
    private static final int PIT_BOTTOM = 460;
    private static final int PIT_LEFT = 40;
    private static final int PIT_RIGHT = 560;

    private static final int MAX_TRIES = 5;
    private static final int FPS = 60;

    // ── Game objects ─────────────────────────────────────────────────
    private final Claw claw;
    private final List<Prize> prizes = new ArrayList<>();
    private final List<Prize> won = new ArrayList<>();
    private int triesLeft = MAX_TRIES;

    // ── Game loop timer ──────────────────────────────────────────────
    private final Timer timer;

    // ── Colours ──────────────────────────────────────────────────────
    private static final Color BG = new Color(30, 30, 50);
    private static final Color PIT_COLOR = new Color(50, 40, 70);
    private static final Color RAIL_COLOR = new Color(160, 160, 160);
    private static final Color TEXT_COLOR = new Color(240, 240, 100);

    private static final Color[] PRIZE_COLORS = {
        new Color(255, 100, 100),
        new Color(100, 200, 255),
        new Color(100, 255, 130),
        new Color(255, 200, 60),
        new Color(220, 130, 255),
        new Color(255, 160, 100),
    };

    public GamePanel() {
        setBackground(BG);
        setFocusable(true);

        claw = new Claw(
            WIDTH / 2.0 - 20,   // start X
            RAIL_Y,             // rail Y
            PIT_LEFT,           // min X
            PIT_RIGHT,          // max X
            PIT_BOTTOM - 50     // max descend Y
        );

        spawnPrizes();

        // Key bindings
        addKeyListener(new KeyAdapter() {
            @Override public void keyPressed(KeyEvent e) { handleKey(e.getKeyCode(), true); }
            @Override public void keyReleased(KeyEvent e) { handleKey(e.getKeyCode(), false); }
        });

        timer = new Timer(1000 / FPS, this);
        timer.start();
    }

    // ── Prize generation ─────────────────────────────────────────────

    private void spawnPrizes() {
        prizes.clear();
        Random rng = new Random();
        int count = 8 + rng.nextInt(5); // 8-12 prizes
        for (int i = 0; i < count; i++) {
            int d = 26 + rng.nextInt(16); // diameter 26-41
            double px = PIT_LEFT + 10 + rng.nextDouble() * (PIT_RIGHT - PIT_LEFT - d - 20);
            double py = PIT_TOP + 10 + rng.nextDouble() * (PIT_BOTTOM - PIT_TOP - d - 20);
            Color c = PRIZE_COLORS[rng.nextInt(PRIZE_COLORS.length)];
            prizes.add(new Prize(px, py, d, c));
        }
    }

    // ── Input ────────────────────────────────────────────────────────

    private void handleKey(int code, boolean pressed) {
        switch (code) {
            case KeyEvent.VK_LEFT, KeyEvent.VK_A  -> claw.setMovingLeft(pressed);
            case KeyEvent.VK_RIGHT, KeyEvent.VK_D -> claw.setMovingRight(pressed);
            case KeyEvent.VK_SPACE, KeyEvent.VK_DOWN, KeyEvent.VK_S -> {
                if (pressed && triesLeft > 0) dropClaw();
            }
            case KeyEvent.VK_R -> { if (pressed) resetGame(); }
        }
    }

    // ── Game loop (called by Timer at ~60 FPS) ───────────────────────

    @Override
    public void actionPerformed(ActionEvent e) {
        claw.update();
        checkGrab();
        checkScored();
        repaint();
    }

    /** When the claw is in GRABBING state, see if its grab zone overlaps a prize. */
    private void checkGrab() {
        if (claw.getState() != Claw.State.GRABBING || claw.getHeldPrize() != null) return;

        var zone = claw.getGrabZone();
        for (Prize p : prizes) {
            if (!p.isGrabbed() && zone.intersects(p.getBounds())) {
                claw.holdPrize(p);
                break;
            }
        }
    }

    /** When the claw returns to IDLE after ascending, score the held prize. */
    private void checkScored() {
        if (claw.getState() != Claw.State.IDLE) return;

        Prize held = claw.getHeldPrize();
        if (held != null) {
            claw.releaseHeldPrize();
            prizes.remove(held);
            won.add(held);
        }
    }

    /** Overridden drop to also count tries. */
    private void dropClaw() {
        if (claw.getState() == Claw.State.IDLE || claw.getState() == Claw.State.MOVING) {
            triesLeft--;
        }
        claw.drop();
    }

    private void resetGame() {
        triesLeft = MAX_TRIES;
        won.clear();
        claw.releaseHeldPrize();
        spawnPrizes();
    }

    // ── Rendering ────────────────────────────────────────────────────

    @Override
    protected void paintComponent(Graphics g0) {
        super.paintComponent(g0);
        Graphics2D g = (Graphics2D) g0;
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        drawBackground(g);
        drawPit(g);
        drawPrizes(g);
        drawRail(g);
        claw.draw(g);
        drawHUD(g);
    }

    private void drawBackground(Graphics2D g) {
        // Gradient-like background
        g.setColor(BG);
        g.fillRect(0, 0, WIDTH, HEIGHT);

        // Glass panel outline
        g.setColor(new Color(80, 80, 120));
        g.drawRect(10, 10, WIDTH - 20, HEIGHT - 20);
    }

    private void drawRail(Graphics2D g) {
        g.setColor(RAIL_COLOR);
        g.fillRect(PIT_LEFT, RAIL_Y - 4, PIT_RIGHT - PIT_LEFT, 8);

        // Rail caps
        g.setColor(RAIL_COLOR.darker());
        g.fillRect(PIT_LEFT - 4, RAIL_Y - 6, 8, 12);
        g.fillRect(PIT_RIGHT - 4, RAIL_Y - 6, 8, 12);
    }

    private void drawPit(Graphics2D g) {
        g.setColor(PIT_COLOR);
        g.fillRoundRect(PIT_LEFT, PIT_TOP, PIT_RIGHT - PIT_LEFT, PIT_BOTTOM - PIT_TOP, 12, 12);

        g.setColor(PIT_COLOR.brighter());
        g.drawRoundRect(PIT_LEFT, PIT_TOP, PIT_RIGHT - PIT_LEFT, PIT_BOTTOM - PIT_TOP, 12, 12);
    }

    private void drawPrizes(Graphics2D g) {
        for (Prize p : prizes) {
            if (!p.isGrabbed()) p.draw(g);
        }
        // Draw the grabbed prize on top
        if (claw.getHeldPrize() != null) {
            claw.getHeldPrize().draw(g);
        }
    }

    private void drawHUD(Graphics2D g) {
        g.setFont(new Font("Monospaced", Font.BOLD, 16));
        g.setColor(TEXT_COLOR);
        g.drawString("Score: " + won.size(), 20, HEIGHT - 15);
        g.drawString("Tries: " + triesLeft, WIDTH / 2 - 40, HEIGHT - 15);

        // Won prizes miniature display
        int startX = WIDTH - 20;
        for (int i = won.size() - 1; i >= 0; i--) {
            startX -= 18;
            g.setColor(PRIZE_COLORS[i % PRIZE_COLORS.length]);
            g.fillOval(startX, HEIGHT - 28, 14, 14);
        }

        // Controls hint
        g.setFont(new Font("Monospaced", Font.PLAIN, 11));
        g.setColor(new Color(150, 150, 170));
        g.drawString("← → move  |  SPACE drop  |  R restart", WIDTH / 2 - 150, 20);

        // Game over
        if (triesLeft <= 0 && claw.getState() == Claw.State.IDLE) {
            g.setFont(new Font("SansSerif", Font.BOLD, 28));
            g.setColor(new Color(255, 80, 80));
            String msg = "GAME OVER – Score: " + won.size();
            int tw = g.getFontMetrics().stringWidth(msg);
            g.drawString(msg, (WIDTH - tw) / 2, HEIGHT / 2 - 40);

            g.setFont(new Font("Monospaced", Font.PLAIN, 14));
            g.setColor(TEXT_COLOR);
            String restart = "Press R to play again";
            tw = g.getFontMetrics().stringWidth(restart);
            g.drawString(restart, (WIDTH - tw) / 2, HEIGHT / 2 - 15);
        }
    }
}
