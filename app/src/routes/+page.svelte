<script lang="ts">
  import { onMount } from 'svelte';
  import { Serialport } from "tauri-plugin-serialport-api";
  import { Button, ButtonGroup, Card } from "flowbite-svelte";
  import { ArrowRightOutline } from "flowbite-svelte-icons";
  import { exit } from '@tauri-apps/api/process';
  import { listen } from '@tauri-apps/api/event';

  interface PlayerData {
    team: number;
    id: number;
    lon: number;
    lat: number;
  }

  interface BallData {
    lon: number;
    lat: number;
  }

  interface SerialData {
    players: PlayerData[];
    ball: BallData;
  }

  let connected: boolean = false;
  let serial_out: SerialData = { players: [], ball: { lon: 0, lat: 0 } };
  let _serial_out: SerialData = { players: [], ball: { lon: 0, lat: 0 } };

  let canvas: HTMLCanvasElement;
  let terminal: HTMLDivElement;
  let current_port: Serialport | null = null;
  let displayed_ports: string[] = [];

  let animationStartTime: number; // Variable to store the animation start time

  let current_positions = {
    players: new Map<number, Player>(),
    ball: null as Ball | null,
  };

  async function connect(port: string) {
    if (port === "Example Connection") {
      connected = true;
      setInterval(simulate_serial_data, 500);
      return;
    }
    try {
      current_port = new Serialport({ path: port, baudRate: 9600 });
      await current_port.open();
      connected = true;
      create_serial_listener();
    } catch (e) {
      console.log(e);
    }
  }

  function latLonToCanvas(lat: number, lon: number, center: { lat: number; lon: number }, canvas: HTMLCanvasElement): { x: number; y: number } {
  // Scaling factor for 0.01 degrees to 100 meters
  const scaleFactor = 1000000;

  // Calculate the x and y positions
  let x = (lon - center.lon) * scaleFactor + (canvas.width / 2);
  let y = (lat - center.lat) * scaleFactor + (canvas.height / 2);

  // Ensure x and y do not go off the canvas
  x = Math.max(0, Math.min(x, canvas.width));
  y = Math.max(0, Math.min(y, canvas.height));

  return { x, y };
}

  function animate() {
    if (!canvas) {
      setTimeout(() => {
        requestAnimationFrame(animate);
      }, 1000);
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const pitch = {
      center: { lat: 0, lon: 0 },
      draw: function (): void {
        const scaleFactor = 10;
        ctx.beginPath();
        ctx.rect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#060";
        ctx.fill();
        ctx.lineWidth = 1;
        ctx.strokeStyle = "#FFF";
        ctx.stroke();
        ctx.closePath();

        ctx.fillStyle = "#FFF";
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0);
        ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, 9.15 * scaleFactor, 0, 2 * Math.PI, false);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, 2, 0, 2 * Math.PI, false);
        ctx.fill();
        ctx.closePath();

        ctx.beginPath();
        ctx.rect(0, (canvas.height - 322) / 2, 132, 322);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.rect(0, (canvas.height - 146) / 2, 44, 146);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.moveTo(1, (canvas.height / 2) - 22);
        ctx.lineTo(1, (canvas.height / 2) + 22);
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.closePath();
        ctx.lineWidth = 1;

        ctx.beginPath();
        ctx.arc(88, canvas.height / 2, 1, 0, 2 * Math.PI, true);
        ctx.fill();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(88, canvas.height / 2, 73, 0.29 * Math.PI, 1.71 * Math.PI, true);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.rect(canvas.width - 132, (canvas.height - 322) / 2, 132, 322);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.rect(canvas.width - 44, (canvas.height - 146) / 2, 44, 146);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.moveTo(canvas.width - 1, (canvas.height / 2) - 22);
        ctx.lineTo(canvas.width - 1, (canvas.height / 2) + 22);
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.closePath();
        ctx.lineWidth = 1;

        ctx.beginPath();
        ctx.arc(canvas.width - 88, canvas.height / 2, 1, 0, 2 * Math.PI, true);
        ctx.fill();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(canvas.width - 88, canvas.height / 2, 73, 0.71 * Math.PI, 1.29 * Math.PI, false);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(0, 0, 8, 0, 0.5 * Math.PI, false);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(0, canvas.height, 8, 0, 2 * Math.PI, true);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(canvas.width, 0, 8, 0.5 * Math.PI, 1 * Math.PI, false);
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(canvas.width, canvas.height, 8, 1 * Math.PI, 1.5 * Math.PI, false);
        ctx.stroke();
        ctx.closePath();
      }
    };

    pitch.draw();

    class Ball {
      x: number;
      y: number;
      targetX: number;
      targetY: number;

      constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
        this.targetX = x;
        this.targetY = y;
      }

      move(): void {
        const coord = latLonToCanvas(_serial_out.ball.lat, _serial_out.ball.lon, pitch.center, canvas);
        this.targetX = coord.x;
        this.targetY = coord.y;
      }

      updatePosition() {
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        this.x += dx * 0.1;
        this.y += dy * 0.1;
        this.draw();
      }

      draw(): void {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 6, 0, 2 * Math.PI, false);
        ctx.fillStyle = "#FFF";
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.stroke();
        ctx.closePath();
      }
    }

    class Player {
      team: number;
      id: number;
      x: number;
      y: number;
      targetX: number;
      targetY: number;

      constructor(team: number, id: number, x: number, y: number) {
        this.team = team;
        this.id = id;
        this.x = x;
        this.y = y;
        this.targetX = x;
        this.targetY = y;
      }

      move(): void {
        const playerData = _serial_out.players.find(p => p.id === this.id && p.team === this.team);
        if (playerData) {
          const coord = latLonToCanvas(playerData.lat, playerData.lon, pitch.center, canvas);
          this.targetX = coord.x;
          this.targetY = coord.y;
        }
      }

      updatePosition() {
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        this.x += dx * 0.1;
        this.y += dy * 0.1;
        this.draw();
      }

      draw(): void {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 10, 0, 2 * Math.PI, false);
        ctx.fillStyle = (this.team === 0) ? "#00F" : "#F00";
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.stroke();
        ctx.closePath();
      }
    }

    const players: Player[] = [];
    _serial_out.players.forEach(p => {
      let player = current_positions.players.get(p.id);
      if (!player) {
        const coord = latLonToCanvas(p.lat, p.lon, pitch.center, canvas);
        player = new Player(p.team, p.id, coord.x, coord.y);
        current_positions.players.set(p.id, player);
      }
      player.move();
      players.push(player);
    });

    if (!current_positions.ball) {
      const ballCoord = latLonToCanvas(_serial_out.ball.lat, _serial_out.ball.lon, pitch.center, canvas);
      current_positions.ball = new Ball(ballCoord.x, ballCoord.y);
    }

    current_positions.ball.move();

    players.forEach(player => player.updatePosition());
    current_positions.ball.updatePosition();

    requestAnimationFrame(animate);
  }

  function create_serial_listener(): void {
    console.log("Reading...");
    listen(`plugin-serialport-read-${current_port?.path}`, (event: { payload: unknown }) => {
      const payload = event.payload as { data: number[] };
      const str = String.fromCharCode.apply(null, payload.data);
      const lines = str.split('\n');

      lines.forEach(line => {
        line = line.trim();
        const parts = line.split(',');
        if (parts.length > 0) {
          const type = parts[0];
          switch (type) {
            case 'red_team':
            case 'blue_team':
              const playerData: PlayerData = {
                team: type === 'red_team' ? 0 : 1,
                id: parseInt(parts[1]),
                lon: parseFloat(parts[2]),
                lat: parseFloat(parts[3]),
              };
              const existingPlayerIndex = _serial_out.players.findIndex(p => p.team === playerData.team && p.id === playerData.id);
              if (existingPlayerIndex > -1) {
                _serial_out.players[existingPlayerIndex] = playerData;
              } else {
                _serial_out.players.push(playerData);
              }
              break;
            case 'ball':
              _serial_out.ball = {
                lon: parseFloat(parts[1]),
                lat: parseFloat(parts[2]),
              };
              break;
            default:
              break;
          }
        }
      });

      serial_out = _serial_out; // Update the serial_out object
      console.log(serial_out); // Log the updated serial_out object
    }).then(unlistener => {
      // unlisten = unlistener;
    });
  }

  async function quit(): Promise<void> {
    console.log("quit");
    await exit(0);
  }

  function simulate_serial_data(): void {
  if (!animationStartTime) {
    animationStartTime = Date.now();
  }

  const elapsedTime = Date.now() - animationStartTime;
  const animationDuration = 10000; // 10 seconds in milliseconds

  // Calculate progress from 0 to 1 based on elapsed time
  const progress = Math.min(elapsedTime / animationDuration, 1);

  // Constants for initial positions and field dimensions
  const fieldWidth = canvas.width;
  const fieldHeight = canvas.height;
  const fieldCenter = { lat: 0, lon: 0 }; // Center at 0 lat, 0 lon
  const playerStartDistance = 110000; // Distance from center to players in meters
  const ballStartDistance = 55000; // Distance from center to ball in meters

  // Initial positions in lat lon
  const initialPlayer1 = {
    lon: 0.0004,
    lat: 0
  };

  const initialPlayer2 = {
    lon: -0.0004,
    lat: 0
  };

  const initialBall = {
    lon: 0,
    lat: 0
  };

  // Calculate current positions based on progress
  let player1: PlayerData = {
    team: 0,
    id: 1,
    lon: initialPlayer1.lon + (fieldCenter.lon - initialPlayer1.lon + 0.0002) * progress * (progress > 0.5 ? 0.5 : 1),
    lat: initialPlayer1.lat + (fieldCenter.lat - initialPlayer1.lat + 0.00002) * progress
  };

  let player2: PlayerData = {
    team: 1,
    id: 2,
    lon: initialPlayer2.lon + (fieldCenter.lon - initialPlayer2.lon) * progress,
    lat: initialPlayer2.lat + (fieldCenter.lat - initialPlayer2.lat) * progress
  };

  let ball: BallData = {
    lon: initialBall.lon + (fieldCenter.lon - initialBall.lon) * progress,
    lat: initialBall.lat + (fieldCenter.lat - initialBall.lat) * progress
  };

  // Player 1 moves towards the center of the field
  // if (progress < 0.5) {
  //   const centerLon = 0;
  //   const centerLat = 0;
  //   player1.lon = initialPlayer1.lon + (centerLon - initialPlayer1.lon) * progress * 3;
  //   player1.lat = initialPlayer1.lat + (centerLat - initialPlayer1.lat) * progress * 2;
  // }

  // Ball moves towards player 2 after player 1 reaches the center
  // if (progress >= 0.5 && progress < 0.75) {
  //   const player2Position = {
  //     lon: initialPlayer2.lon + (fieldCenter.lon - initialPlayer2.lon) * progress,
  //     lat: initialPlayer2.lat + (fieldCenter.lat - initialPlayer2.lat) * progress
  //   };
  //
  //   ball = {
  //     lon: ball.lon + (player2Position.lon - player1.lon) * (progress - 0.5) * 2,
  //     lat: ball.lat + (player2Position.lat - player1.lat) * (progress - 0.5) * 2
  //   };
  // }

  // Player 2 kicks the ball out towards the top edge after stopping it
  if (progress == 1) {
    ball = {
      lon: 0.00006,
      lat: 0.00004
    };
  }

  // Update serial_out with current positions
  _serial_out = {
    players: [player1, player2],
    ball: ball
  };
  serial_out = _serial_out;
}
 
  function update_dynamic(): void {
    get_open_ports().then(data => {
      displayed_ports = data;
      displayed_ports.push("Example Connection"); // Adding mock example connection
    });
  }

  async function get_open_ports(): Promise<string[]> {
    const availablePorts = await Serialport.available_ports();
    return availablePorts;
  }

  update_dynamic(); // Fetch available ports when the app starts

  onMount(() => {
    requestAnimationFrame(animate); // Start the animation loop after the component has mounted
  });
</script>

{#if !connected}
<div class="full-width flex flex-col items-center justify-center">
  <ButtonGroup class="full-width mt-5">
    <Button on:click={update_dynamic}>Update</Button>
    <Button on:click={quit}>Quit</Button>
  </ButtonGroup>
  {#if displayed_ports.length != 0}
    {#each displayed_ports as port}
      <div class="w-1/2 center-margin">
        <Card href="/" size="xl" padding="xl" class="min-w-max mb-5 mt-3">
          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Available Connection</h5>
          <p class="mb-3 font-normal text-gray-700 dark:text-gray-400 leading-tight">Port: {port}</p>
          <Button class="w-fit" on:click={() => connect(port)}>
            Read Serial <ArrowRightOutline class="w-3.5 h-3.5 ml-2 text-white" />
          </Button>
        </Card>
      </div>
    {/each}
  {/if}
  {#if displayed_ports.length == 0}
    <div class="w-1/2 center-margin">
      <Card href="/" size="xl" padding="xl" class="min-w-max mb-5 mt-3">
        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">No available connections (loading...)</h5>
      </Card>
    </div>
  {/if}
</div>
{/if}

{#if connected}
  <div class="w-[calc(100%-2rem)] center-margin">
    <h1 class="full-width center-margin text-center">Current connected port: {current_port?.path || "Example Connection"}</h1>
    <br />
    <canvas bind:this={canvas} class="canvas center-margin" width="800" height="518"></canvas>
    <br />
    <div bind:this={terminal} class="terminal center-margin">
      {JSON.stringify(serial_out, null, 2)}
    </div>
    <br />
    <ButtonGroup divClass="full-width" size="xl">
      <Button on:click={() => { connected = false; if (current_port) current_port.close(); }} class="full-width">Disconnect</Button>
    </ButtonGroup>
  </div>
{/if}

<style>
  .full-width {
    width: 100%;
    min-width: 100%;
  }

  .center-margin {
    margin-left: auto;
    margin-right: auto;
  }

  canvas {
    border: solid 10px #060;
  }

  .terminal {
    background-color: #000;
    color: #FFF;
    height: 200px;
    overflow-y: scroll;
  }
</style>
