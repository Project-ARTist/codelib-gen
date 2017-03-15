// CODE_GENERATOR END //////////////////////////////////////////////////////////////////////////////////////////////////

 private:
  static const std::unordered_set<std::string> METHODS;

 private:
//  // Forbid Class Construction
//  CodeLib() {}
//  explicit CodeLib(CodeLib const&);  // Don't Implement
//  void operator=(CodeLib const&);    // Don't implement

 public:
  // Forbid Class Construction
  explicit CodeLib(CodeLib const&) = delete;
  void operator=(CodeLib const&) = delete;
  // Forbid Class Construction END
};  // class CodeLib

}  // namespace art

#endif  // ART_ENV_CODELIB_H_
