<script>
    import { onMount } from 'svelte';
    import axios from 'axios';
    import MultiSelect from 'svelte-multiselect';
    import { Map, Marker, controls } from '@beyonk/svelte-mapbox';
    
    const mapboxApiKey = process.env.VITE_PUBLIC_MAPBOX_API_KEY;
    const api_end_point = "http://127.0.0.1:5000";
    const { GeolocateControl, NavigationControl, ScaleControl } = controls;

    let schedules = [];
    let poolFilter = [];
    let dayFilter = '';
    let startTimeFilter = '';
    let endTimeFilter = '23:00';
    let swimTypeFilter = []; // New swim type filter
    let swimTypes = []; // Store swim types
    let isStartTimeSortedAsc = true;
    let isPoolSortedAsc = true;
    let isSwimTypeSortedAsc =true;
    let pools = [];
    let poolsDict = {};
    let scriptLog = {};
    let mapComponent;
    let brandColour = "rgb(255, 0, 0)";

    let isMapVisible = true;
    let isDescriptionVisible = false;

    $: {
        console.log("Current poolsDict: ", poolsDict);
        console.log("Map labels: ", Object.values(poolsDict).map(pool => pool.name));
        console.log("Schedules",  schedules);
    }

    function toggleDescriptionVisibility() {
        isDescriptionVisible = !isDescriptionVisible;
    }

    function toggleMapVisibility() {
        isMapVisible = !isMapVisible;
    }

    const fetchLastRunTime = async () => {
        try {
            const response = await axios.get(`${api_end_point}/script-log`);
            scriptLog = response.data;
        } catch (error) {
            console.error('Error fetching pools:', error);
        }
    };

    function addToPoolFilter(poolName) {
        if (!poolFilter.includes(poolName)) {
            poolFilter = [...poolFilter, poolName];
            fetchSchedules(); // Refresh schedules based on new filter
        }
    }

    // Fetching pools from the backend
    const fetchPools = async () => {
        try {
            const response = await axios.get(`${api_end_point}/pools`);
            pools = response.data;
        } catch (error) {
            console.error('Error fetching pools:', error);
        }
    };

    // Fetch swim types from backend
    const fetchSwimTypes = async () => {
        try {
            const response = await axios.get(`${api_end_point}/swim-types`); // Assuming an endpoint for swim types
            swimTypes = response.data; // Store swim types dynamically
        } catch (error) {
            console.error('Error fetching swim types:', error);
        }
    };

    const fetchSchedules = async () => {
        try {
            // Fetch schedules with existing filters
            const response = await axios.get(`${api_end_point}/schedules`, {
                params: { 
                    'pool[]': poolFilter,
                    day: dayFilter,
                    start_time: startTimeFilter,
                    end_time: endTimeFilter,
                }
            });

            // Store fetched schedules
            let fetchedSchedules = response.data;

            // Apply keyword filter for swim types locally
            const keyword = swimTypeFilter.join(' ').toLowerCase(); // Combine filters as a single keyword
            if (keyword) {
                fetchedSchedules = fetchedSchedules.filter(schedule =>
                    schedule.swim_type.toLowerCase().includes(keyword)
                );
            }

            // Update schedules after all filters
            schedules = fetchedSchedules;

            // Rebuild poolsDict to reflect the filtered schedules
            poolsDict = {};
            for (const schedule of schedules) {
                poolsDict[schedule.pool] = {
                    name: schedule.pool,
                    lat: schedule.latitude,
                    lng: schedule.longitude,
                };
            }

            console.log("Updated poolsDict: ", poolsDict);
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

    const sortSchedulesByProperty = (property, isAsc) => {
        schedules = schedules.slice().sort((a, b) => {
            const valueA = a[property].toLowerCase();
            const valueB = b[property].toLowerCase();
            return isAsc ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA);
        });
    };


    onMount(() => {
        fetchSchedules(); // Fetch schedules initially
        fetchPools(); // Fetch pools when the component mounts
        fetchSwimTypes(); // Fetch swim types when the component mounts
        fetchLastRunTime();
        if (mapComponent) {
            mapComponent.setCenter([ '-75.695000', '45.4201'], 4);
        }
    });
    

    function handleRecentre(e) {
        console.log('Map recentered:', e.detail.center);
    }
</script>

<button class="toggle-description-button" on:click={toggleDescriptionVisibility}>
    <img src="../../question-mark-circled-icon.png" alt="Help" class="help-icon" />
</button>
{#if isDescriptionVisible}
<div class="description-box">
    
        <div class="description-content">
            <ul>
                <li>Type in the MultiSelect boxes and select create this option to filter by keywords</li>
                <li>The map displays the facilities' locations based on filtering. Click on find my location on the top left of the map to show where you are.</li>
                <li>Click on a facility name in the table to open the Ottawa Recreation Web Page.</li>
                <!-- Added disclamer -->
                <li style="font-size: 0.7em;">The information contained in this website is based on the City of Ottawa’s website, and may contain errors. Users of the website should make sure they check the schedules with each facility, or their web page.</li>
            </ul>
        </div>
</div>
{/if}

<h1>Ottawa Activity Schedules</h1>

<div class="script-log">
    <p><strong>Last Updated:</strong> {scriptLog.last_run_time ? `${scriptLog.last_run_time} (Script: ${scriptLog.script_name})` : "Fetching..."}</p>
</div>

<div class="filters">
    <div class="filter-container">
        <div class="filter-item">
            <label for="pool-select"><strong>Filter by Facility:</strong></label>
            <MultiSelect
                id="pool-select"
                options={pools}
                placeholder="Select facility"
                bind:selected={poolFilter}
                on:change={fetchSchedules}
                allowUserOptions="append"
                ulSelectedClass="selected-pools"  />
        </div>

        <div class="filter-item">
            <label for="swim-type-select"><strong>Filter by Type:</strong></label>
            <MultiSelect
                id="swim-type-select"
                options={swimTypes}  
                placeholder="Select activity type"
                bind:selected={swimTypeFilter}
                on:change={fetchSchedules}
                allowUserOptions="append"
                ulSelectedClass="selected-activity-types" />
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
                <Marker lat={pool.lat} lng={pool.lng} color={brandColour} >
                    <div class="content" slot="popup">
                      <h3>{pool.name}</h3>
                        <div>
                        <a href="https://www.google.com/maps/search/?api=1&query={pool.name}" target="_blank">
                            {pool.name}
                        </a>
                        </div>
                    </div>
                </Marker>
            {/if}
        {/each}
    </Map>
</div>

<!-- Schedule Table -->
<div class="schedule-table-container">
    <table>
        <thead>
            <tr>
                <th>
                    Facility
                    <button 
                        on:click={() => {
                            sortSchedulesByProperty('pool', isPoolSortedAsc);
                            isPoolSortedAsc = !isPoolSortedAsc;
                        }} 
                        aria-label="Sort by Pool">
                        {isPoolSortedAsc ? '▲' : '▼'}
                    </button>
                </th>
                <th>
                    Ottawa Web Page
                </th>
                <th>
                    Activity Type
                    <button 
                        on:click={() => {
                            sortSchedulesByProperty('swim_type', isSwimTypeSortedAsc);
                            isSwimTypeSortedAsc = !isSwimTypeSortedAsc;
                        }} 
                        aria-label="Sort by Swim Type">
                        {isSwimTypeSortedAsc ? '▲' : '▼'}
                    </button>
                </th>
                <th>Day</th>
                <th>
                    Start Time 
                    <button on:click={sortSchedulesByStartTime} aria-label="Sort by Start Time">
                        {isStartTimeSortedAsc ? '▲' : '▼'}
                    </button>
                </th>
                <th>End Time</th>
            </tr>
        </thead>               
        <tbody>
            {#each schedules as schedule}
                <tr>
                    <td><a href="https://ottawa.ca/en/recreation-and-parks/facilities/place-listing/{schedule.link}" target="_blank">{schedule.pool}</a></td>
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
        width: 75%;  
        margin: 0 auto;
        margin-bottom: 5vh;
    }

    .hidden-map {
        height: 0;
        overflow: hidden;
    }

    .schedule-table-container {
        transition: opacity 0.3s ease;
    }
    .toggle-description-button {
        position: absolute;
        top: 10px;
        left: 10px;
        background: none;
        border: none;
        cursor: pointer;
        padding: 0;
    }

    .help-icon {
        width: 24px; /* Adjust as needed */
        height: 24px; /* Adjust as needed */
    }

    .description-box {
        position: absolute;
        top: 50px; /* Adjusted to appear below the button */
        left: 10px;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        width: 300px; /* Adjusted width for better readability */
        z-index: 200; /* To ensure it sits above other elements */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .description-content ul {
        margin: 0;
        padding-left: 20px;
        font-size: 1em;
    }

    .description-content li {
        margin-top: 10px;
        margin-bottom: 5px;
    }
</style>
