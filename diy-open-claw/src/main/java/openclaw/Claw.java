package openclaw;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Stroke;
import java.awt.geom.Rectangle2D;

/**
 * The claw is a simple state-machine that can:
 *   IDLE      → waiting for player input
 *   MOVING    → sliding left / right along the rail
 *   DESCENDING → dropping toward the prizes
 *   GRABBING  → closing on a prize
 *   ASCENDING → lifting back up (with or without a prize)
 *
 * All positions and speeds are in pixels; the game loop ticks at ~60 FPS.
 */
public class Claw {

    public enum State { IDLE, MOVING, DESCENDING, GRABBING, ASCENDING }

    // Dimensions
    private static final int WIDTH = 40;
    private static final int PRONG_LENGTH = 28;

    // Speeds (pixels per tick)
    private static final double HORIZONTAL_SPEED = 4.0;
    private static final double VERTICAL_SPEED = 3.0;

    // Position
    private double x;       // left edge of the claw housing
    private double y;       // top of the claw housing (on the rail)
    private final double railY;  // fixed Y of the rail

    // Boundaries
    private final double minX;
    private final double maxX;
    private final double maxDescendY;

    // State
    private State state = State.IDLE;
    private boolean movingLeft;
    private boolean movingRight;

    // Grab animation
    private double prongAngle = 30;          // degrees of prong spread
    private static final double OPEN_ANGLE = 30;
    private static final double CLOSED_ANGLE = 5;

    // Attached prize (if any)
    private Prize heldPrize;

    public Claw(double startX, double railY, double minX, double maxX, double maxDescendY) {
        this.x = startX;
        this.y = railY;
        this.railY = railY;
        this.minX = minX;
        this.maxX = maxX;
        this.maxDescendY = maxDescendY;
    }

    // ── Input ────────────────────────────────────────────────────────

    public void setMovingLeft(boolean v)  { this.movingLeft = v; }
    public void setMovingRight(boolean v) { this.movingRight = v; }

    /** Player presses the "drop" button. */
    public void drop() {
        if (state == State.IDLE || state == State.MOVING) {
            state = State.DESCENDING;
            prongAngle = OPEN_ANGLE;
        }
    }

    // ── Update (called each tick) ────────────────────────────────────

    public void update() {
        switch (state) {
            case IDLE, MOVING -> {
                if (movingLeft)  x = Math.max(minX, x - HORIZONTAL_SPEED);
                if (movingRight) x = Math.min(maxX - WIDTH, x + HORIZONTAL_SPEED);
                state = (movingLeft || movingRight) ? State.MOVING : State.IDLE;
            }
            case DESCENDING -> {
                y += VERTICAL_SPEED;
                if (y >= maxDescendY) {
                    state = State.GRABBING;
                }
            }
            case GRABBING -> {
                // Close the prongs over several ticks
                prongAngle -= 2;
                if (prongAngle <= CLOSED_ANGLE) {
                    prongAngle = CLOSED_ANGLE;
                    state = State.ASCENDING;
                }
            }
            case ASCENDING -> {
                y -= VERTICAL_SPEED;
                if (heldPrize != null) {
                    heldPrize.setX(x + WIDTH / 2.0 - heldPrize.getDiameter() / 2.0);
                    heldPrize.setY(y + PRONG_LENGTH);
                }
                if (y <= railY) {
                    y = railY;
                    state = State.IDLE;
                    prongAngle = OPEN_ANGLE;
                }
            }
        }
    }

    // ── Collision ────────────────────────────────────────────────────

    /** Bounding box of the claw tips (used to check prize collision). */
    public Rectangle2D getGrabZone() {
        double gx = x;
        double gy = y + PRONG_LENGTH - 6;
        return new Rectangle2D.Double(gx, gy, WIDTH, 12);
    }

    public State getState() { return state; }

    public void holdPrize(Prize p) {
        this.heldPrize = p;
        p.setGrabbed(true);
    }

    public Prize releaseHeldPrize() {
        Prize p = heldPrize;
        heldPrize = null;
        return p;
    }

    public Prize getHeldPrize() { return heldPrize; }

    public double getX() { return x; }
    public double getY() { return y; }

    // ── Rendering ────────────────────────────────────────────────────

    public void draw(Graphics2D g) {
        Stroke original = g.getStroke();
        double cx = x + WIDTH / 2.0;

        // Cable from rail to claw housing
        g.setColor(Color.GRAY);
        g.setStroke(new BasicStroke(2));
        g.drawLine((int) cx, (int) railY, (int) cx, (int) y);

        // Housing block
        g.setColor(new Color(180, 180, 180));
        g.fillRoundRect((int) x, (int) y, WIDTH, 14, 6, 6);
        g.setColor(Color.DARK_GRAY);
        g.drawRoundRect((int) x, (int) y, WIDTH, 14, 6, 6);

        // Prongs (two angled lines from the centre-bottom of the housing)
        g.setStroke(new BasicStroke(3, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g.setColor(new Color(200, 200, 200));

        double baseY = y + 14;
        double rad = Math.toRadians(prongAngle);

        // Left prong
        int lx = (int) (cx - Math.sin(rad) * PRONG_LENGTH);
        int ly = (int) (baseY + Math.cos(rad) * PRONG_LENGTH);
        g.drawLine((int) cx, (int) baseY, lx, ly);

        // Right prong
        int rx = (int) (cx + Math.sin(rad) * PRONG_LENGTH);
        int ry = ly;
        g.drawLine((int) cx, (int) baseY, rx, ry);

        // Small hooks at the tips
        g.setStroke(new BasicStroke(2));
        g.drawLine(lx, ly, lx + 4, ly + 4);
        g.drawLine(rx, ry, rx - 4, ry + 4);

        g.setStroke(original);
    }
}
