include(ParflowTest)

set(TESTS
    LW_surface_press
    crater2D
    crater2D_vangtable_linear
    crater2D_vangtable_spline
    default_richards_wells
    default_single
    default_single_read_porosity
    forsyth2
    harvey_flow
    harvey_flow_pgs
    indicator_field
    overland_tiltedV_MGSemiTest
    richards_hydrostatic_equilibrium
    small_domain
)

if(${PARFLOW_HAVE_HYPRE})
    list(
        APPEND TESTS
        Dirichlet
        LW_var_dz
        LW_var_dz_spinup
        bc_flux_file
        bc_pressure_file
        channelwidth
        default_overland
        default_richards
        default_richards_nocluster
        default_richards_restart
        octree-large-domain
        octree-simple
        overland_FlatICP
        overland_flux
        overland_octree_performance_rot_0
        overland_octree_performance_rot_45
        overland_slopingslab_DWE
        overland_slopingslab_KWE
        overland_tiltedV_DWE
        overland_tiltedV_KWE
        overland_tiltedV_KWE_top_patch
        overland_tiltedV_KWE_top_patch_2
        overland_tiltedV_KWE_top_patch_3
        pfmg
        pfmg_galerkin
        pfmg_octree
        richards_FBx
        richards_FBy
        richards_box_proctest
        richards_box_proctest_vardz
        smg
        terrain_following_grid_overland
        tilted_v_with_reservoir_overland_flow
        tilted_v_with_reservoir_overland_kinematic
        van-genuchten-file
        var_dz_1D
        var_dz_with_well
        water_balance_x
        water_balance_x.hardflow.jac
        water_balance_x.hardflow.nojac
        water_balance_y
    )
endif()

if(${PARFLOW_HAVE_SILO})
    list(
        APPEND TESTS
        # indicator_field
    )

    if(${PARFLOW_HAVE_HYPRE})
        list(
            APPEND TESTS
            # default_richards_with_silo
        )
    endif()
endif()

if(${PARFLOW_HAVE_NETCDF})
    list(APPEND TESTS indicator_field_netcdf)
    if(${PARFLOW_HAVE_HYPRE})
        #This test is failing on several platforms
        list(
            APPEND TESTS
            #    	default_richards_with_netcdf
            default_richards_restart_netcdf
        )
    endif()
endif()

set(SAMRAI_TESTS)
set(SAMRAI_TESTS_WITH_PATCH_COUNT)

if(${PARFLOW_HAVE_SAMRAI})
    list(APPEND SAMRAI_TESTS samrai_compute_domain)

    list(APPEND SAMRAI_TESTS_WITH_PATCH_COUNT samrai)
endif()

list(APPEND PARALLEL_3DTOPO_TESTS "")
list(APPEND PARALLEL_2DTOPO_TESTS "")

if(${PARFLOW_AMPS_LAYER} IN_LIST PARFLOW_AMPS_LAYER_REQUIRE_MPI)
    list(
        APPEND PARALLEL_3DTOPO_TESTS
        default_single
        default_single_read_porosity
    )

    if(${PARFLOW_HAVE_HYPRE})
        list(
            APPEND PARALLEL_3DTOPO_TESTS
            default_richards
            default_richards_restart
        )

        if(${PARFLOW_HAVE_NETCDF})
            list(APPEND PARALLEL_3DTOPO_TESTS default_richards_restart_netcdf)
        endif()

        list(
            APPEND PARALLEL_2DTOPO_TESTS
            default_overland
            default_overland.pfmg.jac
            default_overland.pfmg_octree.fulljac
            LW_var_dz
            LW_var_dz_spinup
            overland_slopingslab_KWE
            richards_box_proctest_vardz
            reservoir_mpi_test
        )

        if(${PARFLOW_HAVE_SILO})
            list(APPEND PARALLEL_2DTOPO_TESTS default_overland.pfmg_octree.jac)
        endif()
    endif()
endif()

if(${PARFLOW_HAVE_OAS3})
    # Exclude tests that use Richards solver
    set(TESTS "")
    set(PARALLEL_3DTOPO_TESTS "")
    set(PARALLEL_2DTOPO_TESTS "")
    list(APPEND TESTS default_single)
endif()

foreach(inputfile ${TESTS})
    pf_add_py_test(${inputfile})
endforeach()

###################################################################

foreach(inputfile ${PARALLEL_2DTOPO_TESTS})
    pf_add_py_parallel_test(${inputfile} 1 2 1)
    pf_add_py_parallel_test(${inputfile} 2 1 1)
    pf_add_py_parallel_test(${inputfile} 1 4 1)
    pf_add_py_parallel_test(${inputfile} 4 1 1)
endforeach()

foreach(inputfile ${PARALLEL_3DTOPO_TESTS})
    pf_add_py_parallel_test(${inputfile} 1 1 2)
    pf_add_py_parallel_test(${inputfile} 1 2 1)
    pf_add_py_parallel_test(${inputfile} 2 1 1)
    pf_add_py_parallel_test(${inputfile} 1 1 4)
    pf_add_py_parallel_test(${inputfile} 1 4 1)
    pf_add_py_parallel_test(${inputfile} 4 1 1)
    pf_add_py_parallel_test(${inputfile} 2 2 2)
    if(
        NOT (
            (
                (${PARFLOW_HAVE_CUDA})
                OR (${PARFLOW_HAVE_KOKKOS})
                OR (${PARFLOW_HAVE_OMP})
            )
        )
    )
        pf_add_py_parallel_test(${inputfile} 3 3 3)
    endif()
endforeach()

###################################################################

add_subdirectory(new_features)
# add_subdirectory (scenarios)
add_subdirectory(key_validation)

if(${PARFLOW_HAVE_CLM})
    add_subdirectory(clm)
    add_subdirectory(washita)
endif(${PARFLOW_HAVE_CLM})
