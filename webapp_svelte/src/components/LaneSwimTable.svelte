<script>
    import { onMount } from 'svelte';
    import axios from 'axios';
    import MultiSelect from 'svelte-multiselect';

    let schedules = [];
    let poolFilter = [];
    let dayFilter = '';
    let timeFilter = '';
    let isStartTimeSortedAsc = true;
    let pools = [];

    // Fetching pools from the backend
    const fetchPools = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/pools');
            pools = response.data;
        } catch (error) {
            console.error('Error fetching pools:', error);
        }
    };

    const fetchSchedules = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/schedules', {
                params: { 'pool[]': poolFilter, day: dayFilter, time: timeFilter }
            });
            schedules = response.data;
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
    });
</script>

<h1>Ottawa Lane Swim Schedules</h1>

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
            <label for="time-select"><strong>Filter by Time:</strong></label>
            <select id="time-select" bind:value={timeFilter} on:change={fetchSchedules}>
                <option value="">All Times</option>
                {#each ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:00"] as time}
                    <option value={time}>{time}</option>
                {/each}
            </select>
        </div>
    </div>
</div>

<table>
    <thead>
        <tr>
            <th>Pool</th>
            <th>Address</th>
            <th>Swim Type</th>
            <th>Day</th>
            <th on:click={sortSchedulesByStartTime} style="cursor: pointer;">
                Start Time {isStartTimeSortedAsc ? '▲' : '▼'}
            </th>
            <th>End Time</th>
        </tr>
    </thead>
    <tbody>
        {#each schedules as schedule}
            <tr>
                <td>{schedule.pool}</td>
                <td>{schedule.address}</td>
                <td>{schedule.swim_type}</td>
                <td>{schedule.day}</td>
                <td>{schedule.start_time}</td>
                <td>{schedule.end_time}</td>
            </tr>
        {/each}
    </tbody>
</table>

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
     /* Customize the MultiSelect component */
     .svelte-multiselect {
        display: block; /* Make sure multiselect is block */
        width: 100%; /* Make it full width */
    }

    /* Custom styles for selected pools */
    .selected-pools {
        display: block; /* Each selected item in a block */
        margin: 0.5rem 0; /* Add margin for spacing */
    }
</style>
