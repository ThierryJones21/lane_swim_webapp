<script>
    import { onMount } from 'svelte';
    import axios from 'axios';
    import MultiSelect from 'svelte-multiselect';
    import { Map, Marker, controls } from '@beyonk/svelte-mapbox';

    const mapboxApiKey = process.env.VITE_PUBLIC_MAPBOX_API_KEY;
    const { GeolocateControl, NavigationControl, ScaleControl } = controls

    let schedules = [];
    let poolFilter = [];
    let dayFilter = '';
    let startTimeFilter = '';
    let endTimeFilter = '';
    let isStartTimeSortedAsc = true;
    let pools = [];
    let poolsDict = {};
    let scriptLog = {};
    let mapComponent;
    let brandColour = "rgb(255, 0, 0)";

    let isMapVisible = true;

    function toggleMapVisibility() {
        isMapVisible = !isMapVisible;
    }

    const geocodeAddress = async (address) => {
        try {
            console.log(address);
            const geocodeResponse = await axios.get(`https://api.mapbox.com/search/geocode/v6/forward?q=${encodeURIComponent(address)}.json&proximity=-75.695000,45.4201&access_token=${mapboxApiKey}`);
            console.log(geocodeResponse.data.features);
            const features = geocodeResponse.data.features;
            if (features.length > 0) {
                const [lng, lat] = features[0].geometry.coordinates;
                return { lat, lng };
            }
        } catch (error) {
            console.error('Error geocoding address:', error);
        }
        return null;
    };

    // Fetching pools from the backend

    const fetchLastRunTime = async () => {
        try {
            const response = await axios.get("https://lane-swim-webapp.onrender.com/script-log");
            scriptLog = response.data;
        } catch (error) {
            console.error('Error fetching last run time:', error);
        }
    };

    const fetchPools = async () => {
        try {
            const response = await axios.get("https://lane-swim-webapp.onrender.com/pools");
            pools = response.data;
            
        } catch (error) {
            console.error('Error fetching pools:', error);
        }
    };

    const fetchSchedules = async () => {
        try {
            const response = await axios.get("https://lane-swim-webapp.onrender.com/schedules", {
                params: { 'pool[]': poolFilter, day: dayFilter, start_time: startTimeFilter, end_time: endTimeFilter }
            });
            schedules = response.data;

            // Clear and update poolsDict based on the filtered schedules
            poolsDict = {};
            for (const schedule of schedules) {
                const { lat, lng } = await geocodeAddress(schedule.address);
                poolsDict[schedule.pool] = { "name" : schedule.pool, "lat": lat, "lng": lng }; // Add lat/lng to the pool
            }
        } catch (error) {
            console.error('Error fetching schedules:', error);
        }
    };

    const sortSchedulesByStartTime = () => {
        schedules = schedules.slice().sort((a, b) => {
            const timeA = new Date(`1970-01-01T${a.start_time}`);
            const timeB = new Date(`1970-01-01T${b.start_time}`);
            return isStartTimeSortedAsc ? timeA - timeB : timeB - timeA;
        });
        isStartTimeSortedAsc = !isStartTimeSortedAsc;
    };

    onMount(() => {
        fetchPools(); // Fetch pools when the component mounts
        fetchSchedules(); // Fetch schedules initially
        fetchLastRunTime();
        if (mapComponent){
            mapComponent.setCenter([ '-75.695000','45.4201'], 4)
        }
    });

    function handleRecentre(e) {
        console.log('Map recentered:', e.detail.center);
    }
</script>

<h1>Ottawa Lane Swim Schedules</h1>

<div class="script-log">
    <p><strong>Last Updated:</strong> {scriptLog.last_run_time ? `${scriptLog.last_run_time} (Script: ${scriptLog.script_name})` : "Fetching..."}</p>
</div>

<div class="filters">
    <div class="filter-container">
        <div class="filter-item">
            <label for="pool-select"><strong>Filter by Pool:</strong></label>
            <MultiSelect
                id="pool-select"
                options={pools}
                placeholder="Select pools"
                bind:selected={poolFilter}
                on:change={fetchSchedules}
                allowUserOptions="append"
                ulSelectedClass="selected-pools"  />
        </div>

        <div class="filter-item">
            <label for="day-select"><strong>Filter by Day:</strong></label>
            <select id="day-select" bind:value={dayFilter} on:change={fetchSchedules}>
                <option value="">All Days</option>
                {#each ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] as day}
                    <option value={day}>{day}</option>
                {/each}
            </select>
        </div>

        <div class="filter-item">
            <label for="start-time-select"><strong>Start Time:</strong></label>
            <select id="start-time-select" bind:value={startTimeFilter} on:change={fetchSchedules}>
                <option value="">Select Start Time</option>
                {#each ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"] as time}
                    <option value={time}>{time}</option>
                {/each}
            </select>
        </div>
        
        <div class="filter-item">
            <label for="end-time-select"><strong>End Time:</strong></label>
            <select id="end-time-select" bind:value={endTimeFilter} on:change={fetchSchedules}>
                <option value="">Select End Time</option>
                {#each ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"] as time}
                    <option value={time}>{time}</option>
                {/each}
            </select>
        </div>
        
    </div>
</div>

<div>
    <!-- Toggle Button -->
    <button class="toggle-map-button" on:click={toggleMapVisibility}>
        {#if isMapVisible}
            ▲ Hide Map
        {:else}
            ▼ Show Map
        {/if}
    </button>
</div>

<div class="map-container {isMapVisible ? '' : 'hidden-map'}">
    <Map
        accessToken={mapboxApiKey}
        bind:this={mapComponent}
        on:recentre={handleRecentre}
        options={{ scrollZoom: true }}
    >
        <NavigationControl />
        <GeolocateControl options={{ some: 'control-option' }} />
        <ScaleControl />
        
        {#each Object.values(poolsDict) as pool}
            {#if pool.lat && pool.lng}
                <Marker lat={pool.lat} lng={pool.lng} label={pool.name} color={brandColour} />
            {/if}
        {/each}
    </Map>
</div>

<!-- Schedule Table -->
<div class="schedule-table-container">
    <table>
        <thead>
            <tr>
                <th>Pool</th>
                <th>Swim Type</th>
                <th>Day</th>
                <th>Start Time</th>
                <th>End Time</th>
            </tr>
        </thead>
        <tbody>
            {#each schedules as schedule}
                <tr>
                    <td><a href="https://www.google.com/maps/search/?api=1&query={schedule.address}" target="_blank">{schedule.pool}</a></td>
                    <td>{schedule.swim_type}</td>
                    <td>{schedule.day}</td>
                    <td>{schedule.start_time}</td>
                    <td>{schedule.end_time}</td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>


<style>
    /* Basic styling */
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { cursor: pointer; }
    div { margin-bottom: 1rem; }
    
    /* Centering the filters */
    .filters {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1rem;
    }

    .filter-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        justify-content: center; /* Centers the filter items horizontally */
        flex-wrap: wrap; /* Allows wrapping for responsiveness */
        position: sticky; /* Keeps filters locked in place */
        top: 0; /* Position from the top */
        background-color: white; /* Background to ensure visibility */
        z-index: 100; /* Higher z-index to overlay on content */
        padding: 1rem; /* Padding for aesthetics */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
    }

    .filter-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    :global(.mapboxgl-marker){
      cursor: pointer;
    } 
    :global(.mapboxgl-map) {
        height: 100vh;  /* Make the map take full height */
        width: 100%;    /* Make the map take full width */
    }

    .map-container {
        height: 60vh;
        transition: height 0.3s ease;
    }

    .hidden-map {
        height: 0;
        overflow: hidden;
    }

    .schedule-table-container {
        transition: opacity 0.3s ease;
    }
</style>
