
    public:
        ModuleCodeLib() = default;
        ModuleCodeLib(const ModuleCodeLib& other) = default;
        ModuleCodeLib(ModuleCodeLib&& other) = default;

        ~ModuleCodeLib() override = default;

        ModuleCodeLib& operator=(const ModuleCodeLib&) = default;
        ModuleCodeLib& operator=(ModuleCodeLib&&) = default;

        unordered_set<string>& getMethods() const override;
        string& getInstanceField() const override;
        string& getCodeClass() const override;
};  // class ModuleCodeLib


#endif  // ART_MODULES_CHANGEME_CHANGEME_CODELIB_H_
