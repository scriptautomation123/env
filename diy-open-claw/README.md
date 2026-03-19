# 🎮 DIY Open Claw – Build Your Own Arcade Claw Game in Java

A complete, from-scratch, zero-dependency arcade claw machine game built
with **Java Swing**.  No game engine required — just the JDK.

```
  ═════════════ rail ═══════════════
            ┃
          ╔═══╗
          ║   ║  ← claw housing
          ╚╦═╦╝
           ╲ ╱   ← prongs
            V
    ┌────────────────────────┐
    │   ●    ●       ●      │
    │      ●    ●  ●     ●  │  ← prize pit
    │   ●       ●     ●     │
    └────────────────────────┘
      Score: 2   Tries: 3
```

## Quick Start

**Prerequisites:** JDK 11 or later (JDK 21 recommended — already in this
repo's devcontainer).

```bash
# Compile
javac -d out src/main/java/openclaw/*.java

# Run
java -cp out openclaw.OpenClawGame
```

### Controls

| Key | Action |
|-----|--------|
| `←` / `A` | Move claw left |
| `→` / `D` | Move claw right |
| `Space` / `↓` / `S` | Drop claw |
| `R` | Restart game |

---

## How It Works – Step by Step

This section walks through every piece so you can understand and
customise the game.

### 1. Project Structure

```
diy-open-claw/
└── src/main/java/openclaw/
    ├── OpenClawGame.java   ← Entry point & JFrame setup
    ├── GamePanel.java      ← Game loop, rendering, input handling
    ├── Claw.java           ← Claw entity with state machine
    └── Prize.java          ← Prize (toy) objects
```

There are no external libraries — everything uses `javax.swing` and
`java.awt` which ship with every JDK.

### 2. The Game Window (`OpenClawGame.java`)

This is the simplest class.  It creates a `JFrame`, adds the `GamePanel`,
and shows the window:

```java
JFrame frame = new JFrame("🎮 DIY Open Claw");
frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
frame.setResizable(false);

GamePanel panel = new GamePanel();
panel.setPreferredSize(new Dimension(600, 500));
frame.add(panel);
frame.pack();
frame.setLocationRelativeTo(null);
frame.setVisible(true);
```

**Key idea:** `SwingUtilities.invokeLater(...)` ensures everything runs on
the Event Dispatch Thread, which is how Swing avoids threading bugs.

### 3. The Game Loop (`GamePanel.java`)

The loop is driven by a `javax.swing.Timer` firing at 60 FPS:

```java
timer = new Timer(1000 / 60, this); // calls actionPerformed()
timer.start();
```

Each tick:
1. **Update** — move the claw, advance animations
2. **Check collisions** — did the claw grab a prize?
3. **Repaint** — redraw everything

```java
@Override
public void actionPerformed(ActionEvent e) {
    claw.update();
    checkGrab();
    checkScored();
    repaint();
}
```

#### Input Handling

A `KeyAdapter` maps arrow keys / WASD to claw movement:

```java
addKeyListener(new KeyAdapter() {
    @Override
    public void keyPressed(KeyEvent e) {
        handleKey(e.getKeyCode(), true);
    }
    @Override
    public void keyReleased(KeyEvent e) {
        handleKey(e.getKeyCode(), false);
    }
});
```

Using `pressed` / `released` booleans gives smooth continuous movement
instead of stuttery key-repeat behaviour.

### 4. The Claw State Machine (`Claw.java`)

The claw has five states:

```
IDLE ──→ MOVING ──→ DESCENDING ──→ GRABBING ──→ ASCENDING ──→ IDLE
          ↑                                                     │
          └─────────────────────────────────────────────────────┘
```

| State | What happens |
|-------|-------------|
| **IDLE** | Claw sits on the rail, waiting for input |
| **MOVING** | Player is pressing left/right |
| **DESCENDING** | Claw drops straight down toward the pit |
| **GRABBING** | Prongs close (animated over several frames) |
| **ASCENDING** | Claw rises back to the rail (carrying a prize if grabbed) |

The `update()` method is a `switch` on the current state:

```java
case DESCENDING -> {
    y += VERTICAL_SPEED;
    if (y >= maxDescendY) {
        state = State.GRABBING;
    }
}
case GRABBING -> {
    prongAngle -= 2;              // close prongs gradually
    if (prongAngle <= CLOSED_ANGLE) {
        prongAngle = CLOSED_ANGLE;
        state = State.ASCENDING;
    }
}
```

**Collision detection** uses `Rectangle2D.intersects()` — when the claw
is in GRABBING state, its grab zone is checked against every prize's
bounding rectangle.

### 5. Prizes (`Prize.java`)

Each prize is a coloured circle with a cute face drawn using basic
`Graphics2D` calls:

```java
g.fill(new Ellipse2D.Double(x, y, diameter, diameter));  // body
g.drawArc(cx - r, cy, r * 2, r, 200, 140);               // smile
```

Prizes are randomly spawned inside the pit with random sizes (26-41 px)
and colours.

### 6. Rendering

Everything is drawn in `paintComponent()` using Java 2D:

- **Background** — solid dark colour with a glass-panel outline
- **Rail** — a horizontal bar at the top
- **Pit** — rounded rectangle where prizes sit
- **Claw** — housing block + two angled prong lines
- **HUD** — score, tries remaining, controls hint

Anti-aliasing is enabled for smooth curves:
```java
g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
                   RenderingHints.VALUE_ANTIALIAS_ON);
```

---

## Customising the Game

### Change difficulty
In `GamePanel.java`:
- `MAX_TRIES` — number of attempts per game
- Prize count and size range in `spawnPrizes()`

In `Claw.java`:
- `HORIZONTAL_SPEED` / `VERTICAL_SPEED` — how fast the claw moves
- `OPEN_ANGLE` / `CLOSED_ANGLE` — how wide the prongs open/close
- The grab-close rate (`prongAngle -= 2`) — smaller = slower close

### Add sound effects
Use `javax.sound.sampled.Clip` to play `.wav` files on grab/score events.

### Add gravity / physics
Make prizes fall when not grabbed using a simple `y += gravity` each tick,
with floor collision at the pit bottom.

### Convert to a network game
Send claw position over a `java.net.Socket` so a friend can watch.

---

## Building with Maven (optional)

If you prefer Maven, create a `pom.xml`:

```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>open-claw</artifactId>
  <version>1.0-SNAPSHOT</version>
  <properties>
    <maven.compiler.release>21</maven.compiler.release>
  </properties>
</project>
```

Then:
```bash
mvn compile exec:java -Dexec.mainClass="openclaw.OpenClawGame"
```

---

## License

This project is placed in the **public domain** — copy, modify, and share
freely.
