<script lang="ts">
  import { Serialport } from "tauri-plugin-serialport-api";
  import { Button, ButtonGroup, Card } from "flowbite-svelte";
  import { ArrowRightOutline } from "flowbite-svelte-icons";
  import { exit } from '@tauri-apps/api/process';
  import type { UnlistenFn } from '@tauri-apps/api/event';
  import { listen } from '@tauri-apps/api/event';

  interface Port {
    path: string;
    baudRate: number;
    opened_port: Serialport | null;
  }

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

  interface GoalData {
    corners: { lat: number, lon: number }[];
  }

  interface SerialData {
    players: PlayerData[];
    ball: BallData;
    goals: GoalData[];
  }

  let ports: Port[] = [];
  let current_port: Port | null = null;
  let displayed_ports: string[] = [];
  let connected: boolean = false;
  let serial_out: string[] = [];
  let unlisten: UnlistenFn | null = null;
  let _serial_out: SerialData = { players: [], ball: { lon: 0, lat: 0 }, goals: [] };

  let canvas: HTMLCanvasElement;
  let terminal: HTMLDivElement;

  function init_ports(): void {
    ports.forEach(port => {
      if (port.opened_port == null) {
        port.opened_port = new Serialport({ path: port.path, baudRate: port.baudRate });
      }
    });
  }

  function init_port(port: Port): void {
    port.opened_port = new Serialport({ path: port.path, baudRate: port.baudRate });
    open_port(port);
  }

  function connect(port: Port, init: boolean = false): Port {
    try {
      ports.push(port);
      if (init) {
        init_port(port);
      }
    } catch (e) {
      console.log(e);
    }
    return port;
  }

  function send_data(port: Port, data: string): void {
    port.opened_port?.write(data);
  }

  function get_data(port: Port): void {
    port.opened_port?.read().then(data => {
      console.log(data);
    });
  }

  async function get_open_ports(): Promise<string[]> {
    const availablePorts = await Serialport.available_ports();
    return availablePorts;
  }

  function open_port(port: Port): void {
    try {
      port.opened_port?.close();
      port.opened_port?.open();
    } catch (e) {
      console.log(e);
    }
  }

  function open_all_ports(): void {
    ports.forEach(open_port);
  }

  function close_port(port: Port | null): void {
    port?.opened_port?.close();
    current_port = null;
    connected = false;
  }

  function update_dynamic(): void {
    get_open_ports().then(data => {
      displayed_ports = data;
      displayed_ports.push("Example Connection"); // Adding mock example connection
    });
  }

  function parse_serial_data(data: string): void {
    const lines = data.split('\n');
    lines.forEach(line => {
      line = line.trimStart();
      const parts = line.split(' ');
      if (parts.length > 0) {
        const type = parts[0];
        switch (type) {
          case 'player':
            _serial_out.players.push({
              team: parseInt(parts[1]),
              id: parseInt(parts[2]),
              lon: parseFloat(parts[3]),
              lat: parseFloat(parts[4]),
            });
            break;
          case 'ball':
            _serial_out.ball = {
              lon: parseFloat(parts[1]),
              lat: parseFloat(parts[2]),
            };
            break;
          case 'goal':
            const goalCorners = [
              { lon: parseFloat(parts[1]), lat: parseFloat(parts[2]) },
              { lon: parseFloat(parts[3]), lat: parseFloat(parts[4]) },
              { lon: parseFloat(parts[5]), lat: parseFloat(parts[6]) },
              { lon: parseFloat(parts[7]), lat: parseFloat(parts[8]) },
            ];
            _serial_out.goals.push({ corners: goalCorners });
            break;
        }
      }
    });
  }

  function latLonToCanvas(lat: number, lon: number, center: { lat: number, lon: number }, canvas: HTMLCanvasElement): { x: number, y: number } {
    const x = (lon - center.lon) + (canvas.width / 2);
    const y = (lat - center.lat) + (canvas.height / 2);
    return { x, y };
  }

  function render_field(): void {
    if (connected && canvas) {
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const pitch = {
        center: { lat: 0, lon: 0 },
        draw: function (): void {
          if (canvas == null) { return; };
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
          ctx.arc(canvas.width / 2, canvas.height / 2, 73, 0, 2 * Math.PI, false);
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

      class Ball {
        x: number = 0;
        y: number = 0;
        move(): void {
          const coord = latLonToCanvas(_serial_out.ball.lat, _serial_out.ball.lon, pitch.center, canvas);
          this.x = coord.x;
          this.y = coord.y;
          this.draw();
        }
        draw(): void {
          if (!ctx) return;
          ctx.beginPath();
          ctx.arc(this.x, this.y, 3, 0, 2 * Math.PI, false);
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
        pitch: typeof pitch;
        x: number = 0;
        y: number = 0;
        constructor(team: number, id: number) {
          this.team = team;
          this.id = id;
          this.pitch = pitch;
        }

        update(): void {
          const playerData = _serial_out.players.find(p => p.id === this.id && p.team === this.team);
          if (playerData) {
            const coord = latLonToCanvas(playerData.lat, playerData.lon, this.pitch.center, canvas);
            this.x = coord.x;
            this.y = coord.y;
            this.draw();
          }
        }

        draw(): void {
          if (!ctx) return;
          ctx.beginPath();
          ctx.arc(this.x, this.y, 5, 0, 2 * Math.PI, false);
          ctx.fillStyle = (this.team === 0) ? "#00F" : "#F00";
          ctx.fill();
          ctx.strokeStyle = "#000";
          ctx.stroke();
          ctx.closePath();
        }
      }

      type type_pitch = typeof pitch;

      class Goal {
        corners: { lat: number; lon: number }[];
        pitch: type_pitch;
        constructor(corners: { lat: number; lon: number }[], pitch: type_pitch) {
          this.corners = corners;
          this.pitch = pitch;
        }

        draw(): void {
          if (!ctx) return;
          ctx.beginPath();
          const startCoord = latLonToCanvas(this.corners[0].lat, this.corners[0].lon, this.pitch.center, canvas);
          ctx.moveTo(startCoord.x, startCoord.y);
          for (let i = 1; i < this.corners.length; i++) {
            const coord = latLonToCanvas(this.corners[i].lat, this.corners[i].lon, this.pitch.center, canvas);
            ctx.lineTo(coord.x, coord.y);
          }
          ctx.closePath();
          ctx.strokeStyle = "#FFF";
          ctx.stroke();
        }
      }

      function drawField() {
        pitch.draw();

        const players: Player[] = [];
        for (let i = 0; i < _serial_out.players.length; i++) {
          players.push(new Player(_serial_out.players[i].team, _serial_out.players[i].id));
        }

        const ball = new Ball();

        const goals: Goal[] = [];

        for (let i = 0; i < _serial_out.goals.length; i++) {
          goals.push(new Goal(_serial_out.goals[i].corners, pitch));
        }

        ball.move();
        players.forEach(player => player.update());
        // Comment out the rendering of goals
        // goals.forEach(goal => goal.draw());
      }

      function updateField() {
        const intervalId = setInterval(() => {
          if (connected) {
            drawField();
          } else {
            clearInterval(intervalId);
          }
        }, 1000);
      }

      updateField();
    }
  }

  async function quit(): Promise<void> {
    console.log("quit");
    await exit(0);
  }

  function update_terminal(): void {
    if (connected) {
      current_port?.opened_port?.read();
    }
  }

  function create_serial_listener(): void {
    console.log("Reading...");
    listen(`plugin-serialport-read-${current_port?.path}`, (event: { payload: unknown }) => {
      const payload = event.payload as { data: number[] };
      const str = String.fromCharCode.apply(null, payload.data);
      const cleanStr = str.replace(/(\r\n|\n|\r)/gm, "");
      parse_serial_data(cleanStr);
      serial_out.push(cleanStr + " ");
      console.log(serial_out);
      terminal.scrollTop = terminal.scrollHeight;
    }).then(unlistener => {
      unlisten = unlistener;
    });
  }

  // Function to simulate receiving serial data for testing
  function simulate_serial_data(): void {
    const mockData = `
      player 0 1 30.5 50.5
      player 1 2 40.5 60.5
      ball 35.5 55.5
      goal -5 -5 5 -5 5 5 -5 5
      goal -5 105 5 105 5 115 -5 115
    `;
    parse_serial_data(mockData);
    render_field();
  }

  update_dynamic();

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
          <Button class="w-fit" on:click={() => { 
            if (port === "Example Connection") {
              current_port = { path: port, baudRate: 9600, opened_port: null }; 
              connected = true; 
              setTimeout(() => { 
                simulate_serial_data(); 
                render_field(); 
                update_terminal(); 
              }, 1000);
            } else {
              current_port = connect({ path: port, baudRate: 9600, opened_port: null }, true); 
              connected = true; 
              setTimeout(() => { 
                create_serial_listener(); 
                render_field(); 
                update_terminal(); 
              }, 1000);
            }
          }}>
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
    <h1 class="full-width center-margin text-center">Current connected port: {current_port?.path}</h1>
    <br />
    <canvas bind:this={canvas} class="canvas center-margin" width="800" height="518"></canvas>
    <br />
    <div bind:this={terminal} class="terminal center-margin">
      {serial_out.join(' ')}
    </div>
    <br />
    <ButtonGroup divClass="full-width" size="xl">
      <Button on:click={() => close_port(current_port)} class="full-width">Disconnect</Button>
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
